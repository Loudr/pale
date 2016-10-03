pale
----

[![Circle CI](https://circleci.com/gh/Loudr/pale/tree/master.svg?style=shield)](https://circleci.com/gh/Loudr/pale/tree/master)

Pale is a python API layer, named after the P in IPA.


It's designed to make implementing and maintaining APIs easy, with convenient
support for versioning, generating documentation from code, and modularity.

Pale is framework-independent, and should be usable with Flask and webapp2


### Status

Pale is currently in an early pre-release state, but we've decided to
open it up now anyways.  As we progress, the interfaces for using Pale
will stabilize, and we'll get our unit tests up to snuff so that you'll
feel confident using Pale in your own projects.

### Contributing

To contribute code:
  1. Fork the repo
  2. Add an issue (if it doesn't exist already) and create a feature branch that include the issue number, like `support_cors-13` for issue #13. 
  3. Write code and make commits locally, then push to your fork. 
  4. Submit a pull request from the feature branch on your fork to the master branch of this repo. Make sure to include `Closes <issue-number>` to close the issue you're working on.
 
### Versioning

We're using `bumpversion` to increment the version number. This is done after the changes made in a feature branch are pulled into the master branch. Once you've followed the steps in Contributing above, switch to your local master branch and enter this in your terminal:
```
bumpversion patch
```
This will automatically increment the version on the patch level (like from `0.9.17` to `0.9.18`) and make a commit.

Next, run `git push` to update the master version.

And then: `git push --tags` to update the version tags on `master`.

### Running Tests

Per the included `circle.yml`, you can use CircleCI to build and test your changes.

You can also run all the tests locally with:

```Shell
nosetests tests/
```

Or run any individual test with:
```Shell
nosetests <path-to-test>
```
