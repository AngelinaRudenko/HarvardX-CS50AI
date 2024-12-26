import os
import random
import re
import sys

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
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transitions = dict()

    pages_count = len(corpus)
    linked_pages_count = len(corpus[page])

    # if no linked pages, choose randomly among all pages with equal probability
    if (linked_pages_count == 0):
        equal_probability = 1 / pages_count

        for filename in corpus:
            transitions[filename] = equal_probability
        
        return

    # probability that random page was chosen
    random_page_probability = (1 - damping_factor) / pages_count

    # iterate over all pages and give them initial probabylity
    # as they were chosen randomly
    for filename in corpus:
        transitions[filename] = random_page_probability

    # probability that linked page was chosen
    linked_pages_probability = damping_factor / linked_pages_count

    # each linked page could be chosen randomly (it's inital state)
    # now add the probability that it was chosen NOT randomly
    for linked_page in corpus[page]:
        transitions[linked_page] +=  linked_pages_probability

    return transitions


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pagerank = dict()

    # iterate over all pages and give them initial cout of visits
    for filename in corpus:
        pagerank[filename] = 0

    # choose first page (sample) randomly
    current_page = random.choice(list(corpus.keys()))
    visited_pages_count = 0
    
    while (visited_pages_count <= n):
        visited_pages_count += 1

        # mark page as visited
        pagerank[current_page] += 1
        transitions = transition_model(corpus, current_page, damping_factor)

        next_pages = list(transitions.keys())
        next_probabilities = list(transitions.values())

        current_page = random.choices(next_pages, weights=next_probabilities)[0]

    # convert visits counts to probabilities
    for filename in pagerank:
        pagerank[filename] /= n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    old_pagerank = dict()
    new_pagerank = dict()

    pages_count = len(corpus)
    equal_probability = 1 / pages_count
    random_page_probability = (1 - damping_factor) / pages_count

    # assign each page equal rank
    for page in corpus:
        new_pagerank[page] = equal_probability

    max_difference = 1

    # this process should repeat until no PageRank value changes by more than 0.001
    # between the current rank values and the new rank values.
    while (max_difference > 0.001):
        old_pagerank = new_pagerank.copy()

        for page in corpus:
            # sum of probabilities to chose current page from incoming pages
            temp = 0

            for link_from in corpus:

                # page that has no links at all should be interpreted as having one link 
                # for every page in the corpus (including itself)
                if len(corpus[link_from]) == 0:
                    temp += old_pagerank[link_from] / pages_count

                # link_from links to page
                elif page in corpus[link_from]:
                    temp += old_pagerank[link_from] / len(corpus[link_from])
            
            new_pagerank[page] = random_page_probability + (damping_factor * temp)

        max_difference = max([abs(new_pagerank[x] - old_pagerank[x]) for x in old_pagerank])

    return old_pagerank


if __name__ == "__main__":
    main()
