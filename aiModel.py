from libraries import *

X = torch.tensor(splitBatchesToXYTensors()[0], dtype=torch.float32)
y = torch.tensor(splitBatchesToXYTensors()[1], dtype=torch.float32)

class tradingWala(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(2, 256),
            nn.Sigmoid(),
            nn.Linear(256, 128),
            nn.Sigmoid(),
            nn.Linear(128, 64),
            nn.Sigmoid(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)


# Create the model, loss function, and optimizer
model = tradingWala()
loss_function = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)

# Training loop
epochs = 20000
for epoch in range(epochs):
    # Forward pass
    output = model(X)
    loss = loss_function(output, y)

    # Backward pass and optimization
    optimizer.zero_grad()  # Zero the gradients
    loss.backward()  # Compute the gradients
    optimizer.step()  # Update the parameters of our network

    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

"""
# Test the model
with torch.no_grad():
    test_output = model(X)
    predictions = (test_output >= 0.5).float()
    print("\nFinal Predictions:")
    for i in range(len(X)):
        print(
            f"Input: {X[i].numpy()}, Predicted: {predictions[i].item():.0f}, Actual: {y[i].item():.0f}"
        )
"""