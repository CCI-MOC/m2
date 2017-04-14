# Developer Guidelines

This document describes the developer policies and procedures for maintaining
Bare Metal Imaging Service (BMI), including the accepted [coding style](#Coding-style).

## Getting started

If you are new to BMI and would like to jump in, then welcome!

Contributions can come in many forms: installing BMI and using it in your
environment (and giving us feedback), improving the testing, squashing bugs and
introducing new functionality.

If you are interested in any of this, a good place to start is by reading the
documentation (linked from the [Readme](./README.html)).

If you're looking to code, there are a few ways to help:
* Improving the BMI documentation
* Better testing
* Reviewing [Pull Requests](https://github.com/CCI-MOC/ims/pulls)
* Discussions on open github issues. 

## Communicating

* IRC: The MOC team hangs out on #moc on [freenode](https://www.freenode.net/)
* IRL (In Real Life): The MOC group office is on the BU campus, at 3 Cummington Mall, Boston, MA room 451. Anyone interested in BMI is welcome to drop in and work there.
* Slack: Our slack channel is at team-bmis.slack.com

## Coding style/conventions

By default, BMI (like many other python projects) uses
[PEP8](https://www.python.org/dev/peps/pep-0008/) as its naming guide, and
[PEP257](https://www.python.org/dev/peps/pep-0257/) for documentation.
Departures are acceptable when called for, but should be discussed first.


## Submitting code / Pull Requests

Overall, BMI follows the [github fork & pull
model](http://scottchacon.com/2011/08/31/github-flow.html) to integrate
contributions, where users fork the main BMI (ims) repo, push changes
to their personal fork and then create a Pull Request to merge it
into the master branch of the BMI repository.

### Prior to the pull request

This summarizes what should be done prior to a pull request:

- [ ] If functionality could have architectural implications or controversial, have a discussion with the team. Ideally, prior to coding to save effort.
- [ ] Ensure any user, deployer or developer documentation is updated.
- [ ] If a change affects an external API, be sure to update docs/rest\_api.md.
- [ ] Ensure tests pass (coming soon!) after making your changes.
- [ ] Ensure that your code is pep8 compliant. 

#### Get agreement from the BMI team

The BMI project appreciates all ideas and submissions. In the past, we've
discussed several alternatives to how things currently work (which we're trying
to get better about writing down), and it would be good to have agreement that
includes input from these past discussions as well as the wisdom of the
community. The best way to do this is to [file an
issue](https://github.com/CCI-MOC/ims/issues) on github, or speak with one of the core developers directly.


#### Testing


Testing helps to ensure the quality of the code base. Every pull request
submitted should first be tested to ensure that all existing tests pass.

When introducing new functionality, new tests (both unit and more comprehensive)
should be added that provide adequate coverage.

If fixing a bug, a regression test should accompany the bug fix to ensure that
the bug does not return.

Once the checklist above has been met, open a Pull Request from your
personal fork to the main BMI repo.

Checkout the [testing document](testing.md) for more details.


### Code review

Code reviews help increase code quality by finding:
* mistakes that can oftentimes be overlooked by a single developer
* improving readability
* helping reviewers to learn about different areas of the code

Reviewers are the final guardians for good code quality. If you see a piece of
complex code, that is probably where you want to spend a lot of your review
time. Remember the 80/20 rule (80% of the bugs come from 20% of the code).


### Approval criteria on github

Pull Requests require at least 2 approvals, also known as "+1"'s, in
order to be merged, with at least 2 core developers being involved in some way:
either as a submitter or a reviewer.

The exception to this is documentation, where we are a little more lenient in
the interest of lowering the barrier to having better docs. For docs changes,
typically one +1 is sufficient.

Whomever provides the enabling +1 is responsible for clicking the merge button
on github. If you do not have commit access, then please add your +1 to the PR
and ask one of the Core Developers to complete the merge.

