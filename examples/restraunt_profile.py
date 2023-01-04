import cProfile
import pstats

from restraunt import main as restraunt_run


def main():
    with cProfile.Profile() as pr:
        restraunt_run()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()
    stats.dump_stats("restraunt_perf.prof")


if __name__ == "__main__":
    main()
