import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_dist = {}
    if corpus[page] == None:
        prob_dist = {key: round(1 / len(corpus), 2) for key in corpus}
        return prob_dist
    else:
        overall_prob = round(
            (1 - damping_factor) / len(corpus), 2
        )  # The probability to be included in each page rank, (Point number 2)
        for key, value in corpus.items():
            prob_dist[key] = prob_dist.get(key, 0) + overall_prob
            if key == page:
                for linked_page in value:
                    prob_dist[linked_page] = prob_dist.get(linked_page, 0) + (
                        damping_factor / len(value)
                    )
    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict.fromkeys(corpus, 0)
    last_generated_sample = random.choice(list(corpus.keys()))  # Starting Random Page
    page_rank[last_generated_sample] += 1  # Adding the sample
    for _ in range(n - 1):
        # Getting Prob Distribution via transition model
        links_with_pd = transition_model(
            corpus=corpus, page=last_generated_sample, damping_factor=damping_factor
        )
        # Choosing the best prob from Prob Distribution via random.choices
        last_generated_sample = random.choices(
            list(links_with_pd.keys()), weights=list(links_with_pd.values()), k=1
        )[0]
        page_rank[last_generated_sample] += 1  # Adding the sample
    # Marginalizing the data from 0 to 1
    pd_page_rank = {key: value / n for key, value in page_rank.items()}
    return pd_page_rank


def numlinks(corpus, page):
    """
    Simple function which return number of links of a certain page
    """

    if page in corpus:
        return len(corpus[page])
    else:
        return None


def get_page_rank(corpus: dict, page_rank: dict, page, damping_factor):
    """
    Returns the pagerank of the given page
    It will calculate from the already calculated page rank of all the pages
    """

    # Traversing through each page in corpus
    summation = 0
    for curr_page, linked_pages in corpus.items():

        # If a page has no links then its going to add the probabily according to the following rule
        if len(linked_pages) == 0:
            summation += page_rank[curr_page] / len(corpus)

        # If a certain page has link to Given page, then following rule is going to be followed
        elif page in linked_pages:
            summation += page_rank[curr_page] / numlinks(corpus, curr_page)

    return (1 - damping_factor) / len(corpus) + (summation * damping_factor)


def check_values(pr_1, pr_2):
    """
    Return True if the difference between values is less than 0.001
    """
    for page in pr_1.keys():
        if pr_1[page] - pr_2[page] > 0.001:
            return False
    return True


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict.fromkeys(corpus, 1 / len(corpus))
    new_page_rank = copy.deepcopy(page_rank)
    while True:
        copied_pr = copy.deepcopy(new_page_rank)
        for page in page_rank.keys():
            new_page_rank[page] = get_page_rank(corpus, copied_pr, page, damping_factor)
        if check_values(new_page_rank, copied_pr):
            return new_page_rank


if __name__ == "__main__":
    main()
