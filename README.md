# Sample E&M Physics IPython Notebook

## Dependencies

The following are required for these examples:

 * Python 3.4

## Instructions

The following will set up a local matplotlib environment for you, and start an
IPython Notebook server:

```bash
  $ make
```

At which point a browser window will open, with a view of this notebook.

Subsequent runs need only do the following:

```bash
  $ make run
```

Unless new dependencies were added to ``requirements.txt``, in which case you
will want to do this:

```bash
  $ make deps && make run
```
