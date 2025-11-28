"""
Silent Gradient Death in Deep Networks
Demonstrates gradient flow issues that TensorGuard detects.

This file intentionally contains GRADIENT DEATH PATTERNS for demonstration.
Running `demyst tensor examples/deep_learning_gradient_death.py` will detect these.

Philosophy: "If the gradient dies in silence, the model learns nothing."
"""

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not installed. This example demonstrates code patterns only.")


# ==============================================================================
# ERROR 1: Deep Sigmoid Chain (Vanishing Gradients)
# ==============================================================================

class DeepSigmoidNetwork(nn.Module):
    """
    WRONG: Deep chain of Sigmoid activations without residual connections.

    Sigmoid saturates at 0 and 1, where gradient approaches zero.
    With 10 layers of Sigmoid, gradients vanish exponentially.
    Early layers receive essentially zero gradient and stop learning.

    TensorGuard detects: gradient_death_chain (CRITICAL)
    Threshold: 3+ consecutive Sigmoid activations
    """

    def __init__(self, input_dim=100, hidden_dim=50, num_layers=10):
        super().__init__()

        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(input_dim, hidden_dim))

        for _ in range(num_layers - 2):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))

        self.layers.append(nn.Linear(hidden_dim, 10))

        # ERROR: Using Sigmoid everywhere
        self.activation = nn.Sigmoid()  # TensorGuard flags this pattern

    def forward(self, x):
        for layer in self.layers[:-1]:
            x = self.activation(layer(x))  # Gradient death chain!
        return self.layers[-1](x)


# ==============================================================================
# ERROR 2: Deep Tanh Network (Less Severe but Still Problematic)
# ==============================================================================

class DeepTanhNetwork(nn.Module):
    """
    WRONG: Deep Tanh chain (slightly better than Sigmoid, still problematic).

    Tanh also saturates at -1 and 1. While centered around 0 (better than
    Sigmoid), it still causes vanishing gradients in deep networks.

    TensorGuard detects: gradient_death_chain (WARNING)
    Threshold: 4+ consecutive Tanh activations
    """

    def __init__(self, input_dim=100, hidden_dim=50, num_layers=8):
        super().__init__()

        self.layers = nn.ModuleList()
        for i in range(num_layers):
            in_features = input_dim if i == 0 else hidden_dim
            out_features = 10 if i == num_layers - 1 else hidden_dim
            self.layers.append(nn.Linear(in_features, out_features))

        self.activation = nn.Tanh()  # TensorGuard: 4+ Tanh in chain

    def forward(self, x):
        for layer in self.layers[:-1]:
            x = self.activation(layer(x))  # Gradient death risk
        return self.layers[-1](x)


# ==============================================================================
# ERROR 3: BatchNorm with track_running_stats=False
# ==============================================================================

class UnstableBatchNormNetwork(nn.Module):
    """
    WRONG: BatchNorm with track_running_stats=False.

    During evaluation, this will use batch statistics instead of
    learned running statistics. This causes:
    1. Non-deterministic behavior (results depend on batch composition)
    2. Distribution shift masked between train and deploy

    TensorGuard detects: unstable_batch_stats (WARNING)
    """

    def __init__(self, input_dim=100, hidden_dim=50):
        super().__init__()

        self.fc1 = nn.Linear(input_dim, hidden_dim)
        # ERROR: track_running_stats=False causes eval-time instability
        self.bn1 = nn.BatchNorm1d(hidden_dim, track_running_stats=False)
        self.fc2 = nn.Linear(hidden_dim, 10)

    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        return self.fc2(x)


# ==============================================================================
# CORRECT: Residual Network (Gradient-Preserving)
# ==============================================================================

class CorrectResidualNetwork(nn.Module):
    """
    CORRECT: Deep network with residual connections.

    Skip/residual connections allow gradients to flow directly from
    output to early layers, solving the vanishing gradient problem.
    This is why ResNet revolutionized deep learning.
    """

    def __init__(self, input_dim=100, hidden_dim=100, num_blocks=10):
        super().__init__()

        self.input_proj = nn.Linear(input_dim, hidden_dim)

        self.blocks = nn.ModuleList()
        for _ in range(num_blocks):
            self.blocks.append(nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),  # Non-saturating activation
                nn.Linear(hidden_dim, hidden_dim)
            ))

        self.output = nn.Linear(hidden_dim, 10)

    def forward(self, x):
        x = self.input_proj(x)

        for block in self.blocks:
            x = x + block(x)  # RESIDUAL CONNECTION - gradients can skip!

        return self.output(x)


# ==============================================================================
# CORRECT: Modern Activation Functions
# ==============================================================================

class ModernActivationNetwork(nn.Module):
    """
    CORRECT: Using GELU/SiLU instead of Sigmoid/Tanh.

    Modern activations like GELU (used in GPT/BERT) and SiLU (used in
    EfficientNet) don't have the saturation problems of Sigmoid/Tanh.
    """

    def __init__(self, input_dim=100, hidden_dim=50, num_layers=10):
        super().__init__()

        self.layers = nn.ModuleList()
        for i in range(num_layers):
            in_features = input_dim if i == 0 else hidden_dim
            out_features = 10 if i == num_layers - 1 else hidden_dim
            self.layers.append(nn.Linear(in_features, out_features))

        self.activation = nn.GELU()  # Non-saturating, smooth

    def forward(self, x):
        for layer in self.layers[:-1]:
            x = self.activation(layer(x))  # No gradient death
        return self.layers[-1](x)


def demonstrate_gradient_death():
    """Numerically show gradient magnitudes through layers."""
    if not TORCH_AVAILABLE:
        print("PyTorch required for numerical demonstration.")
        return

    print("\n" + "=" * 60)
    print("NUMERICAL GRADIENT ANALYSIS")
    print("=" * 60)

    # Create models
    bad_model = DeepSigmoidNetwork()
    good_model = CorrectResidualNetwork()

    # Create sample input
    x = torch.randn(32, 100, requires_grad=True)

    # Forward + backward for bad model
    bad_output = bad_model(x)
    bad_loss = bad_output.sum()
    bad_loss.backward()

    print("\nDeepSigmoidNetwork (WRONG):")
    print("Gradient magnitudes by layer:")
    for i, layer in enumerate(bad_model.layers):
        if hasattr(layer, 'weight') and layer.weight.grad is not None:
            grad_norm = layer.weight.grad.norm().item()
            status = "VANISHING!" if grad_norm < 1e-6 else ""
            print(f"  Layer {i}: {grad_norm:.2e} {status}")

    # Reset gradients
    x.grad = None

    # Forward + backward for good model
    good_output = good_model(x)
    good_loss = good_output.sum()
    good_loss.backward()

    print("\nCorrectResidualNetwork (CORRECT):")
    print("Gradient magnitudes by block:")
    print(f"  Input projection: {good_model.input_proj.weight.grad.norm().item():.2e}")
    for i, block in enumerate(good_model.blocks):
        grad_norm = block[0].weight.grad.norm().item()
        print(f"  Block {i}: {grad_norm:.2e}")


if __name__ == "__main__":
    print("=" * 60)
    print("GRADIENT DEATH DEMONSTRATION")
    print("=" * 60)

    print("""
This example demonstrates patterns that cause 'silent gradient death'
where neural networks appear to train but early layers learn nothing.

TensorGuard detects:
1. gradient_death_chain: 3+ Sigmoid or 4+ Tanh without residuals
2. unstable_batch_stats: BatchNorm with track_running_stats=False
3. normalization_before_sensitive: BatchNorm before attention layers
""")

    if TORCH_AVAILABLE:
        demonstrate_gradient_death()
    else:
        print("\nInstall PyTorch to see numerical demonstration:")
        print("  pip install torch")

    print("\n" + "=" * 60)
    print("Run: demyst tensor examples/deep_learning_gradient_death.py")
    print("to see TensorGuard detect these patterns automatically.")
    print("=" * 60)
