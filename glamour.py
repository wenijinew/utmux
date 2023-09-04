#!/usr/bin/env python3
"""Provide utility functions for Tmux option reading and writing."""

import shlex
import subprocess

import yaml
from loguru import logger
from yaml import Loader

logger.add("glamour.py.log", rotation="10MB")

UTF_8 = "utf-8"
EMPTY = ""

# tmux options
STYLE_START = "#["
STYLE_END = "]"


def get(_dict, key, default):
    """'Rewrite' get method of dict.

    When value is None or Empty, use default.
    Should be used in theme configuration only.
    Lower theme configuration could reuse upper level them configuration, then
    it's possible to configure less items.
    However, user configuration should be able to overwrite theme
    configuration.
    For example, if theme defined icons, but user don't want to use icon, then
    they can set icon as Empty.
    """
    value = _dict.get(key)
    if value is None or value.strip() == EMPTY:
        value = default
    return value


class Theme(dict):
    """Wrapper for theme configuration."""

    def __init__(self, theme_config: dict):
        self.status_line = theme_config.get("status_line")
        self.status_left = ThemeStatusLeft(theme_config)
        self.active_window = ThemeWindow(
            self.status_line, theme_config.get("window").get("active")
        )
        self.inactive_window = ThemeWindow(
            self.status_line, theme_config.get("window").get("inactive")
        )
        self.window = {
            "active": self.active_window,
            "inactive": self.inactive_window,
        }
        self.status_right = ThemeStatusRight(theme_config)
        super().__init__(
            status_line=self.status_line,
            status_left=self.status_left,
            window=self.window,
            status_right=self.status_right,
        )


class ThemeStatusLeft(dict):
    """Wrapper for status_left configuration."""

    def __init__(self, theme_config):
        """Constructor"""
        status_line = theme_config.get("status_line")
        status_left = theme_config.get("status_left")
        self.fg_option = get(
            status_left, "fg_option", status_line.get("foreground")
        )
        self.bg_option = get(
            status_left, "bg_option", status_line.get("background")
        )
        self.fg_icon = get(
            status_left, "fg_icon", status_line.get("foreground")
        )
        self.bg_icon = get(
            status_left, "bg_icon", status_line.get("background")
        )
        self.fg_decorator = status_left.get(
            "fg_decorator", status_line.get("foreground")
        )
        self.bg_decorator = get(
            status_left, "bg_decorator", status_line.get("background")
        )
        self.icon = get(status_left, "icon", status_line.get("left_icon"))
        self.decorator = status_left.get(
            "decorator", status_line.get("left_decorator")
        )
        self.style = get(status_left, "style", status_line.get("style"))
        super().__init__(
            fg_option=self.fg_option,
            bg_option=self.bg_option,
            fg_icon=self.fg_icon,
            bg_icon=self.bg_icon,
            fg_decorator=self.fg_decorator,
            bg_decorator=self.bg_decorator,
            icon=self.icon,
            decorator=self.decorator,
            style=self.style,
        )


class ThemeWindow(dict):
    """Wrapper for window configuration."""

    def __init__(self, status_line_theme_config, window_theme_config):
        """Constructor"""
        self.fg_window = get(
            window_theme_config,
            "fg_window",
            status_line_theme_config.get("foreground"),
        )
        self.bg_window = get(
            window_theme_config,
            "bg_window",
            status_line_theme_config.get("background"),
        )
        self.fg_window_index = get(
            window_theme_config,
            "fg_window_index",
            status_line_theme_config.get("foreground"),
        )
        self.bg_window_index = get(
            window_theme_config,
            "bg_window_index",
            status_line_theme_config.get("background"),
        )
        self.fg_icon = get(
            window_theme_config,
            "fg_icon",
            status_line_theme_config.get("foreground"),
        )
        self.bg_icon = get(
            window_theme_config,
            "bg_icon",
            status_line_theme_config.get("background"),
        )
        self.fg_decorator = get(
            window_theme_config,
            "fg_decorator",
            status_line_theme_config.get("foreground"),
        )
        self.bg_decorator = get(
            window_theme_config,
            "bg_decorator",
            status_line_theme_config.get("background"),
        )
        self.icon = get(
            window_theme_config,
            "icon",
            status_line_theme_config.get("left_icon"),
        )
        self.decorator = get(
            window_theme_config,
            "decorator",
            status_line_theme_config.get("left_decorator"),
        )
        self.style = get(
            window_theme_config, "style", status_line_theme_config.get("style")
        )
        super().__init__(
            fg_window=self.fg_window,
            bg_window=self.bg_window,
            fg_window_index=self.fg_window_index,
            bg_window_index=self.bg_window_index,
            fg_icon=self.fg_icon,
            bg_icon=self.bg_icon,
            fg_decorator=self.fg_decorator,
            bg_decorator=self.bg_decorator,
            icon=self.icon,
            decorator=self.decorator,
            style=self.style,
        )


class ThemeStatusRight(dict):
    """Wrapper for status_right configuration."""

    def __init__(self, theme_config):
        """Constructor"""
        status_line = theme_config.get("status_line")
        status_right = theme_config.get("status_right")
        self.fg_option = get(
            status_right, "fg_option", status_line.get("foreground")
        )
        self.bg_option = get(
            status_right, "bg_option", status_line.get("background")
        )
        self.fg_icon = get(
            status_right, "fg_icon", status_line.get("foreground")
        )
        self.bg_icon = get(
            status_right, "bg_icon", status_line.get("background")
        )
        self.fg_decorator = get(
            status_right, "fg_decorator", status_line.get("foreground")
        )
        self.bg_decorator = get(
            status_right, "bg_decorator", status_line.get("background")
        )
        self.icon = get(status_right, "icon", status_line.get("left_icon"))
        self.decorator = get(
            status_right, "decorator", status_line.get("left_decorator")
        )
        self.style = get(status_right, "style", status_line.get("style"))
        super().__init__(
            fg_option=self.fg_option,
            bg_option=self.bg_option,
            fg_icon=self.fg_icon,
            bg_icon=self.bg_icon,
            fg_decorator=self.fg_decorator,
            bg_decorator=self.bg_decorator,
            icon=self.icon,
            decorator=self.decorator,
            style=self.style,
        )


class Constructor:
    """Constructor for status line component."""

    def __init__(self, catppuccin: dict, theme: Theme):
        """Constructor"""
        self.general = catppuccin.get("general")
        self.status_line = catppuccin.get(
            "status_line", theme.get("status_line")
        )
        self.foreground = self.status_line.get("foreground")
        self.background = self.status_line.get("background")
        self.status_left = catppuccin.get("status_left")
        self.window = catppuccin.get("window")
        self.status_right = catppuccin.get("status_right")
        self.theme = theme

    def produce_general_options_commands(self):
        """Produce general options."""
        general = []
        for name, value in self.general.get("options").items():
            if name.startswith("_"):
                name = f"@{name.lstrip('_')}"
            general.append(f"set-option -gq {name} '{value}'")

        for name, component in self.general.get("styles").items():
            if name == "option-commands":
                continue
            foreground = get(
                component, "fg", self.status_line.get("foreground")
            )
            background = get(
                component, "bg", self.status_line.get("background")
            )
            style = get(component, "style", self.status_line.get("style"))
            style_command = self.get_style_command(
                foreground, background, style, name
            )
            general.append(style_command)

        return ";".join(general)

    def produce_status_line(self):
        """Produce status line option"""
        fg_status_line = self.foreground
        bg_status_line = self.background
        return f"fg={fg_status_line},bg={bg_status_line}"

    def produce_status_left(self):
        """Produce status left option string"""
        status_left = []
        for component in self.status_left.values():
            enabled = component.get("enabled", "on")
            if not enabled:
                continue
            tmux_option = component.get("tmux_option", EMPTY)
            icon = component.get("icon", self.theme.status_left.get("icon"))
            decorator = component.get(
                "decorator", self.theme.status_left.get("decorator")
            )
            fg_option = component.get(
                "fg_option", self.theme.status_left.get("fg_option")
            )
            bg_option = component.get(
                "bg_option", self.theme.status_left.get("bg_option")
            )
            fg_icon = component.get(
                "fg_icon", self.theme.status_left.get("fg_icon")
            )
            bg_icon = component.get(
                "bg_icon", self.theme.status_left.get("bg_icon")
            )
            fg_decorator = component.get(
                "fg_decorator", self.theme.status_left.get("fg_decorator")
            )
            bg_decorator = component.get(
                "bg_decorator", self.theme.status_left.get("bg_decorator")
            )
            style = component.get("style", self.theme.status_left.get("style"))
            tmux_option_style = f"{self.get_style_for_option(fg_option, bg_option, style, tmux_option)}"
            icon_style = (
                f"{self.get_style_for_option(fg_icon, bg_icon, style, icon)}"
            )
            decorator_style = f"{self.get_style_for_option(fg_decorator, bg_decorator, style, decorator)}"
            component_value = (
                f"{icon_style}{decorator_style}{tmux_option_style}"
            )
            status_left.append(component_value)

        return " ".join(status_left)

    def produce_window(self):
        """Return tuple with active window and inactive window option strings"""
        windows = {}
        for name, component in self.window.items():
            style = component.get(
                "style", self.theme.window.get(name).get("style")
            )
            icon = component.get(
                "icon", self.theme.window.get(name).get("icon")
            )
            decorator = component.get(
                "decorator", self.theme.window.get(name).get("decorator")
            )
            window_name = component.get(
                "window_name", self.theme.window.get(name).get("window_name")
            )
            window_index = component.get(
                "window_index",
                self.theme.window.get(name).get("window_index"),
            )
            decorator = component.get(
                "decorator", self.theme.window.get(name).get("decorator")
            )

            fg_icon = component.get(
                "fg_icon", self.theme.window.get(name).get("fg_icon")
            )
            bg_icon = component.get(
                "bg_icon", self.theme.window.get(name).get("bg_icon")
            )
            fg_decorator = component.get(
                "fg_decorator", self.theme.window.get(name).get("fg_decorator")
            )
            bg_decorator = component.get(
                "bg_decorator", self.theme.window.get(name).get("bg_decorator")
            )
            fg_window = component.get(
                "fg_window", self.theme.window.get(name).get("fg_window")
            )
            bg_window = component.get(
                "bg_window", self.theme.window.get(name).get("bg_window")
            )
            fg_window_index = component.get(
                "fg_window_index",
                self.theme.window.get(name).get("fg_window_index"),
            )
            bg_window_index = component.get(
                "bg_window_index",
                self.theme.window.get(name).get("bg_window_index"),
            )

            window_style = self.get_style_for_option(
                fg_window, bg_window, style, window_name
            )
            window_index_style = self.get_style_for_option(
                fg_window_index, bg_window_index, style, window_index
            )
            icon_style = self.get_style_for_option(
                fg_icon, bg_icon, style, icon
            )
            decorator_style = self.get_style_for_option(
                fg_decorator, bg_decorator, style, decorator
            )
            component_value = f"{window_style}{window_index_style}{icon_style}{decorator_style} "
            windows[name] = component_value

        return windows

    def produce_status_right(self):
        """Produce status right tmux options string."""
        status_right = []
        for options in self.status_right.values():
            enabled = options.get("enabled", "on")
            if not enabled:
                continue
            tmux_option = options.get("tmux_option", EMPTY)
            icon = options.get("icon", self.theme.status_right.get("icon"))
            decorator = options.get(
                "decorator", self.theme.status_right.get("decorator")
            )
            fg_option = options.get(
                "fg_option", self.theme.status_right.get("fg_option")
            )
            bg_option = options.get(
                "bg_option", self.theme.status_right.get("bg_option")
            )
            fg_icon = options.get(
                "fg_icon", self.theme.status_right.get("fg_icon")
            )
            bg_icon = options.get(
                "bg_icon", self.theme.status_right.get("bg_icon")
            )
            fg_decorator = options.get(
                "fg_decorator", self.theme.status_right.get("fg_decorator")
            )
            bg_decorator = options.get(
                "bg_decorator", self.theme.status_right.get("bg_decorator")
            )
            style = options.get("style", self.theme.status_right.get("style"))
            tmux_option_style = f"{self.get_style_for_option(fg_option, bg_option, style, tmux_option)}"
            icon_style = (
                f"{self.get_style_for_option(fg_icon, bg_icon, style, icon)}"
            )
            decorator_style = f"{self.get_style_for_option(fg_decorator, bg_decorator, style, decorator)}"
            component_value = (
                f"{decorator_style}{icon_style}{tmux_option_style}"
            )
            status_right.append(component_value)

        return " ".join(status_right)

    def get_style_for_option(self, foreground, background, style, option):
        """construct style string with foreground and background"""
        if option is None:
            option = ""
        pieces = []
        if foreground:
            pieces.append(f"fg={foreground}")
        if background:
            pieces.append(f"bg={background}")
        pieces.append(style)
        _style = f"{STYLE_START}{','.join(pieces)}{STYLE_END}{option}"

        pieces = []
        if foreground:
            pieces.append(f"fg={self.foreground}")
        if background:
            pieces.append(f"bg={self.background}")
        pieces.append(style)
        _default_style = f"{STYLE_START}{','.join(pieces)}{STYLE_END}"
        return f"{_style}{_default_style}"

    def get_style_command(self, foreground, background, style, style_name):
        return f"set-option {style_name} 'fg={foreground},bg={background},{style}'"

    def produce_option_command(self, option, value):
        """Return tmux set option command"""
        return f"set-option -gq {option} '{value}'"

    def produce_option_commands(self):
        """Return all tmux set option commands."""
        status_line = self.produce_status_line()
        status_left = self.produce_status_left()
        window = self.produce_window()
        status_right = self.produce_status_right()

        status_line_cmd = self.produce_option_command(
            "status-style", status_line
        )
        status_left_cmd = self.produce_option_command(
            "status-left", status_left
        )
        active_window_cmd = self.produce_option_command(
            "window-status-current-format", window["active"]
        )
        inactive_window_cmd = self.produce_option_command(
            "window-status-format", window["inactive"]
        )
        status_right_cmd = self.produce_option_command(
            "status-right", status_right
        )
        general_commands = self.produce_general_options_commands()
        option_commands = []
        option_commands.append(general_commands)
        option_commands.append(status_line_cmd)
        option_commands.append(status_left_cmd)
        option_commands.append(active_window_cmd)
        option_commands.append(inactive_window_cmd)
        option_commands.append(status_right_cmd)
        return option_commands


def glamour(config_file="glamour.yaml"):
    """Load config file, overwrite options by value from tmux.conf."""
    # TODO: the config file should be customizable by putting under
    # $HOME/.tmux/catppuccin.yaml
    set_option_commands = []
    dynamic_config_file_name = get_tmux_option(
        "dynamic_config_file_name", config_file
    )
    with open(dynamic_config_file_name, "r", encoding=UTF_8) as config:
        catppuccin = yaml.load(config, Loader=Loader)

        theme_name = catppuccin.get("theme")
        dynamic_theme_name = get_tmux_option("dynamic_theme_name", theme_name)
        theme_filename = f"{dynamic_theme_name}.theme.yaml"
        with open(theme_filename, "r", encoding=UTF_8) as theme_file:
            theme_config = yaml.load(theme_file, Loader=Loader)
            theme = Theme(theme_config)

            constructor = Constructor(catppuccin, theme)
            set_option_commands = constructor.produce_option_commands()
    return ";".join(set_option_commands)


def main():
    """Run"""
    set_option_commands = glamour()
    if set_option_commands:
        for command in set_option_commands.split(";"):
            run_shell_command(f"tmux {command}")


def get_tmux_option(option_name, default_value):
    """Read tmux option."""
    assert option_name is not None, "option_name is None!"
    assert default_value is not None, "default_value is None!"

    if not option_name.startswith("@"):
        option_name = f"@{option_name}"
    shell_cmd = f'tmux show-option -gqv "{option_name}"'
    return run_shell_command(shell_cmd, default_value)


def run_shell_command(command, default_output=None):
    """Run shell command."""
    try:
        command_args = shlex.split(command)
        value = (
            subprocess.check_output(command_args, shell=False)
            .decode(UTF_8)
            .strip()
        )
        if value is not None and value.strip() != EMPTY:
            return value
        return default_output
    except Exception:
        logger.opt(exception=True).debug(
            f"{command} is failed to run. use default value: \
                                         {default_output} as output."
        )
        return default_output


if __name__ == "__main__":
    main()