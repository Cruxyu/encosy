# encosy
## [Docs](https://cruxyu.github.io/encosy/)

## Installation

### Using pip
Releases of `encosy` can be installed using pip::

    $ pip install encosy

Source releases and any binaries can be downloaded from the PyPI link.

    https://pypi.org/project/encosy/


### Using git and poetry
For poetry guide follow [this link](https://python-poetry.org/docs/)::
    
    git clone https://github.com/Cruxyu/encosy.git
    poetry install

### Profiling
#### CPU
To create a profile.prof

    from file_with_app import app
    import cProfile
    import pstats
    
    
    def main():
        with cProfile.Profile() as pr:
            app()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        # stats.print_stats()
        stats.dump_stats("app.prof")
    
    
    if __name__ == "__main__":
        main()

To see viz of a profile

    poetry run python -m snakeviz app.prof

#### Memory
To test memory run

    mprof run app.py  

To see the results run
    
    mprof plot

