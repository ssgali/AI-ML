import csv
import itertools
import sys
from copy import deepcopy

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }
    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False if row["trait"] == "0" else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene: set, two_genes: set, have_trait: set):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # Initial Joint Probability
    total_probability = 1

    # Zero Gene Set
    zero_gene = set(people.keys()).difference(one_gene.union(two_genes))

    # First off, we are going to start with the one_gene
    for person in list(one_gene):
        if has_parent(person, people):
            total_probability *= one_gene_joint_probability(
                person, people, one_gene, two_genes
            )
        else:
            total_probability *= PROBS["gene"][1]

    for person in list(two_genes):
        if has_parent(person, people):
            total_probability *= two_genes_joint_probability(
                person, people, one_gene, two_genes
            )
        else:
            total_probability *= PROBS["gene"][2]

    for person in list(zero_gene):
        if has_parent(person, people):
            total_probability *= zero_gene_joint_probability(
                person, people, one_gene, two_genes
            )
        else:
            total_probability *= PROBS["gene"][0]

    # Handling all the persons using have_trait and people
    for person in people.keys():
        if person in have_trait:
            total_probability *= set_trait_probability(
                person, one_gene, two_genes, True
            )
        else:
            total_probability *= set_trait_probability(
                person, one_gene, two_genes, False
            )

    return total_probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # Adding J_P to one_gene of every person in the list
    for person in list(one_gene):
        probabilities[person]["gene"][1] += p

    # Adding J_P to two_genes of every person in the list
    for person in list(two_genes):
        probabilities[person]["gene"][2] += p

    # Adding J_P to zero_gene of every person in the list
    for person in list(set(probabilities.keys()).difference(one_gene.union(two_genes))):
        probabilities[person]["gene"][0] += p

    # Adding J_P to trait of every person in the list
    for person in list(have_trait):
        probabilities[person]["trait"][True] += p

    # Adding J_P to no_trait of every person in the list
    for person in list(set(probabilities.keys()).difference(have_trait)):
        probabilities[person]["trait"][False] += p


def normalize(probabilities: dict):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    prob_copy = deepcopy(probabilities)
    for person, probs in prob_copy.items():
        for types, prob_set in probs.items():
            for key, value in prob_set.items():
                probabilities[person][types][key] = value / sum(prob_set.values())


def has_parent(person: str, family_dict: dict):
    """
    Tell whether a person in family_dict has a parent(mother and father).
    """
    return (family_dict[person]["father"] != None) and (
        family_dict[person]["mother"] != None
    )


def helper(parent, one_gene, two_genes):
    """
    Checks in which set the parent is in, then calculates the probability regarding the gene.
    Returns the Success rate of transfering the Gene to offspring.
    """
    if parent in one_gene:  # One Gene means chance is 0.5
        return 0.5
    elif parent in two_genes:  # Two Genes Success rate is 1, but mutation might reverse
        return 1 - PROBS["mutation"]
    else:  # Zero Gene meaning no gene transfer, but mutation might reverse
        return PROBS["mutation"]


def two_genes_joint_probability(person, people, one_gene, two_genes):
    """
    The prob of person having one gene from parent 1 and another gene from parent 2.
    P(2_g) = P(A AND B)
    Where A = 1 Gene from Father
    B = 1 Gene from Mother
    """
    # father_prob = Prob of getting gene from father
    # mother_prob = Prob of getting gene from mother

    father_prob = helper(people[person]["father"], one_gene, two_genes)
    mother_prob = helper(people[person]["mother"], one_gene, two_genes)
    return father_prob * mother_prob


def zero_gene_joint_probability(person, people, one_gene, two_genes):
    """
    The prob of person having no gene from any parent.
    P(0_g) = P(~A AND ~B)
    Where, ~A = No Gene from Father
    ~B = No Gene from Mother
    """
    # father_prob = Prob of getting gene from father
    # mother_prob = Prob of getting gene from mother
    father_prob = 1 - helper(people[person]["father"], one_gene, two_genes)
    mother_prob = 1 - helper(people[person]["mother"], one_gene, two_genes)
    return father_prob * mother_prob


def one_gene_joint_probability(person, people, one_gene, two_genes):
    """
    The prob of person having one gene from any one parent
    P(2_g) = P(A AND ~B) OR P(~A AND B)
    Where A = 1 Gene from Father
    B = 1 Gene from Mother
    """
    # father_prob = Prob of getting gene from father
    # mother_prob = Prob of getting gene from mother
    father_prob = helper(people[person]["father"], one_gene, two_genes)
    mother_prob = helper(people[person]["mother"], one_gene, two_genes)

    return (mother_prob * (1 - father_prob)) + (father_prob * (1 - mother_prob))


def set_trait_probability(person, one_gene, two_genes, trait_status):
    """
    Updates the Given Joint Probability based on the trait_status of a person and gene
    it belongs too.
    """
    if person in one_gene:
        return PROBS["trait"][1][trait_status]
    elif person in two_genes:
        return PROBS["trait"][2][trait_status]
    else:
        return PROBS["trait"][0][trait_status]


if __name__ == "__main__":
    main()
