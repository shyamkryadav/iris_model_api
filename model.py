import pandas as pd 
from sklearn.preprocessing import StandardScaler 
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load data
df = pd.read_csv('iris.csv')

# Check data
print(df.head())

# Define features and target
X = df[["sepal_length", "sepal_width", "petal_length", "petal_width"]]
Y = df["species"]
print(X)
print(Y)

# Split the data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Initialize and fit scaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)  # Corrected: Apply transform on X_test

# Initialize and fit classifier
classifier = RandomForestClassifier()
classifier.fit(X_train, Y_train)

# Save the model and scaler
pickle.dump(classifier, open("model.pkl", "wb"))
pickle.dump(sc, open("scaler.pkl", "wb"))  # Save scaler for use in API
