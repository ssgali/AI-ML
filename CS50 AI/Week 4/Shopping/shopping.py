import csv
import sys
from csv import DictReader

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

date_to_int = {
    "Jan": 0,
    "Feb": 1,
    "Mar": 2,
    "Apr": 3,
    "May": 4,
    "June": 5,
    "Jul": 6,
    "Aug": 7,
    "Sep": 8,
    "Oct": 9,
    "Nov": 10,
    "Dec": 11,
}

# Data Splitting Constant
TEST_SIZE = 0.4

# Number of Neighbours in KNN
NEIGHBOURS = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []
    with open(filename) as csvfile:
        loaded_data = DictReader(csvfile)
        for row in loaded_data:

            # Adding to Labels dataset
            labels.append(1 if row["Revenue"] == "True" else 0)

            # Converting to Integer Dataset

            row["Month"] = date_to_int[row["Month"]]
            row["VisitorType"] = 1 if row["VisitorType"] == "Returning_Visitor" else 0
            row["Weekend"] = 1 if row["Weekend"] == "True" else 0
            row["Administrative"] = int(row["Administrative"])
            row["Administrative_Duration"] = float(row["Administrative_Duration"])
            row["Informational"] = int(row["Informational"])
            row["Informational_Duration"] = float(row["Informational_Duration"])
            row["ProductRelated"] = int(row["ProductRelated"])
            row["ProductRelated_Duration"] = float(row["ProductRelated_Duration"])
            row["BounceRates"] = float(row["BounceRates"])
            row["ExitRates"] = float(row["ExitRates"])
            row["PageValues"] = float(row["PageValues"])
            row["SpecialDay"] = float(row["SpecialDay"])
            row["OperatingSystems"] = int(row["OperatingSystems"])
            row["Browser"] = int(row["Browser"])
            row["Region"] = int(row["Region"])
            row["TrafficType"] = int(row["TrafficType"])

            # -['1'] index for removing revenue
            # Since its not needed and is a Label
            #
            #

            rows_values = (list(row.values()))[:-1]

            evidence.append(rows_values)

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    model = KNeighborsClassifier(n_neighbors=NEIGHBOURS)

    # Training the model

    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    # Total number of correct predictions
    total_negative_labels = 0
    total_positive_labels = 0

    # Total number of Actual predictions
    true_postive_preds = 0
    true_negative_preds = 0

    for label, pred in zip(labels, predictions):
        if label == 0:
            total_negative_labels += 1
            if pred == 0:
                true_negative_preds += 1
        else:
            total_positive_labels += 1
            if pred == 1:
                true_postive_preds += 1

    # Division by zero check
    if total_negative_labels != 0:
        specificity = float(true_negative_preds / total_negative_labels)
    else:
        specificity = 0

    if total_positive_labels != 0:
        sensitivity = float(true_postive_preds / total_positive_labels)
    else:
        sensitivity = 0
    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
