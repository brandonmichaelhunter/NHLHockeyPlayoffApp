# NHLHockeyPlayoffApp
A repo to host my NHL Hockey Playoff App

# Install PyEnv
What is PyEnv?
- PyEnv is tool that allows you to switch between multiple version of Python from your desktop.
- Install instructions
#### MacOS

<details>

The options from the [Linux section above](#linuxunix) also work but Homebrew is recommended for basic usage.

##### [Homebrew](https://brew.sh) in macOS

   1. Update homebrew and install pyenv:
      ```sh
      brew update
      brew install pyenv
      ```
      If you want to install (and update to) the latest development head of Pyenv
      rather than the latest release, instead run:
      ```sh
      brew install pyenv --head
      ```
   3. Then follow the rest of the post-installation steps, starting with
      [Set up your shell environment for Pyenv](#b-set-up-your-shell-environment-for-pyenv).

   4. OPTIONAL. To fix `brew doctor`'s warning _""config" scripts exist outside your system or Homebrew directories"_

      If you're going to build Homebrew formulae from source that link against Python
      like Tkinter or NumPy
      _(This is only generally the case if you are a developer of such a formula,
      or if you have an EOL version of MacOS for which prebuilt bottles are no longer provided
      and you are using such a formula)._

      To avoid them accidentally linking against a Pyenv-provided Python,
      add the following line into your interactive shell's configuration:

      * Bash/Zsh:

        ~~~bash
        alias brew='env PATH="${PATH//$(pyenv root)\/shims:/}" brew'
        ~~~

      * Fish:

        ~~~fish
        alias brew="env PATH=(string replace (pyenv root)/shims '' \"\$PATH\") brew"
        ~~~
</details>

#### Windows

<details>

Pyenv does not officially support Windows and does not work in Windows outside
the Windows Subsystem for Linux.
Moreover, even there, the Pythons it installs are not native Windows versions
but rather Linux versions running in a virtual machine --
so you won't get Windows-specific functionality.

If you're in Windows, we recommend using @kirankotari's [`pyenv-win`](https://github.com/pyenv-win/pyenv-win) fork --
which does install native Windows Python versions.

</details>

### B. Set up your shell environment for Pyenv
----

The below setup should work for the vast majority of users for common use cases.
See [Advanced configuration](#advanced-configuration) for details and more configuration options.

#### Bash
  <details>

  Stock Bash startup files vary widely between distributions in which of them source
  which, under what circumstances, in what order and what additional configuration they perform.
  As such, the most reliable way to get Pyenv in all environments is to append Pyenv
  configuration commands to both `.bashrc` (for interactive shells)
  and the profile file that Bash would use (for login shells).

  1. First, add the commands to `~/.bashrc` by running the following in your terminal:

      ```bash
      echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
      echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
      echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
      ```
  2. Then, if you have `~/.profile`, `~/.bash_profile` or `~/.bash_login`, add the commands there as well.
     If you have none of these, create a `~/.profile` and add the commands there.

     * to add to `~/.profile`:
       ``` bash
       echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
       echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
       echo 'eval "$(pyenv init - bash)"' >> ~/.profile
       ```
     * to add to `~/.bash_profile`:
       ```bash
       echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
       echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
       echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile
       ```

   **Bash warning**: There are some systems where the `BASH_ENV` variable is configured
   to point to `.bashrc`. On such systems, you should almost certainly put the
   `eval "$(pyenv init - bash)"` line into `.bash_profile`, and **not** into `.bashrc`. Otherwise, you
   may observe strange behaviour, such as `pyenv` getting into an infinite loop.
   See [#264](https://github.com/pyenv/pyenv/issues/264) for details.
   
   </details>
   
#### Zsh
  
  <details>
  Add Pyenv startup commands to `~/.zshrc` by running the following in your terminal:
  
  ```zsh
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
  echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
  echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
  ```
  
  If you wish to get Pyenv in noninteractive login shells as well, also add the commands to `~/.zprofile` or `~/.zlogin`.
  </details>
----
# Make sure you have Python version 3.12 installed
- Run ```pyenv install 3.12.0`` within your terminal.
# Set Pythyon version
```pyenv shell 3.12.00```

# Install FAST API
- What is Fast API? web framework for building APIs with Python.
- Install Fast API: 
    - ```pip install virtualenv``` or (using pyenv-virtualenv) ```brew install pyenv-virtualenv```
    - ```pyenv virtualenv 3.12.0 redlobstercheesybiscuit```
    - ```pyenv activate redlobstercheesybiscuit```
    - ```pip install fastapi```
# Create your directory structure
``` mkdir apps/api/hockeyplayoffapi```
``` cd apps/api/hockeyplayoffapi```
# Create your main.py file: ```touch main.py```
# Update main.py with your code.
# Run FastAPI dev in your terminal: ```fastapi dev ``` 
