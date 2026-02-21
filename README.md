# Alpha Trading Framework --- CLI Manual

## Overview

This document explains how to use the console commands inside the Alpha
Trading Framework project.

The framework includes a simple command dispatcher that maps user
console input to Python functions.

------------------------------------------------------------------------

## How Commands Work

Commands are registered in the dispatcher like this:

``` python
COMMANDS = {
    "get_or_create_security": get_or_create_security_id,
    "get_security_id": get_security_id
}
```

This means:

-   When you type `get_or_create_security`, the function
    `get_or_create_security_id` is executed.
-   When you type `get_security_id`, the function `get_security_id` is
    executed.

------------------------------------------------------------------------

## Command Format

All commands follow this format:

    command_name key=value

Arguments must be written as:

    key=value

⚠ Incorrect format example:

    get_security_id RTS

✔ Correct format example:

    get_security_id name=RTS

------------------------------------------------------------------------

## Available Commands

### 1. get_or_create_security

**Description:**\
Returns the security ID if it exists.\
If it does not exist, it creates a new security and returns its ID.

**Usage:**

    get_or_create_security name=RTS

**Example:**

    get_or_create_security name=GAZP

------------------------------------------------------------------------

### 2. get_security_id

**Description:**\
Returns the ID of an existing security.

**Usage:**

    get_security_id name=RTS

**Example:**

    get_security_id name=GAZP

If the security exists, its ID will be returned.\
If it does not exist, the system will return an error or empty result
depending on implementation.

------------------------------------------------------------------------

## How to Run the Console

1.  Open terminal
2.  Navigate to project directory
3.  Run:

```{=html}
<!-- -->
```
    python main.py

If console loop is enabled, you will see:

    Async console ready. Type 'exit' to quit.

To exit the console:

    exit

------------------------------------------------------------------------

## Summary

  Command                  Purpose
  ------------------------ -------------------------------
  get_or_create_security   Create or fetch a security ID
  get_security_id          Fetch existing security ID

------------------------------------------------------------------------

This manual helps developers understand how the internal CLI dispatcher
works and how to properly enter commands.

