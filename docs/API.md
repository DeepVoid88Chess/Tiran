# TIRAN API

## Compiler API

compile_tiran(source, target=None) compiles TIRAN source. If target is omitted, the compiler reads the convert directive.
format_tiran(source) normalizes TIRAN indentation while preserving statements.
TiranError is raised for invalid syntax, unsupported target features, malformed names, and unclosed blocks.

## Roblox/Luau API

### Services

    service Players = Players
    service ReplicatedStorage = ReplicatedStorage
    service RunService = RunService

Generates game:GetService(...).

### Instances

    create part Part
    create folder Folder
    create model Monsters
    create remoteevent MonsterEvent
    create remote_function Request
    create bindableevent Signal
    create screengui GameGui
    create frame Panel
    create textlabel Title
    create textbutton PlayButton

These generate Instance.new(...) calls.

### Properties and parenting

    set Part.name = "Spawn"
    set Part.anchored = true
    set Part.position = Vector3.new(0, 5, 0)
    set player.Character.Humanoid.WalkSpeed = 20
    parent Part to workspace

Property names are converted to Roblox-style PascalCase on assignment.

### Events and remotes

    connect Part.Touched to onTouched
    disconnect connection
    fire MonsterEvent "spawn"
    invoke Request "get_state"

connect generates :Connect(...). fire and invoke target RemoteEvent/RemoteFunction server calls.

### Math constructors

    vector3 spawn = 0, 5, 0
    cframe camera = 0, 10, 0

These generate Vector3.new(...) and CFrame.new(...).

### Timing and cleanup

    wait 1
    destroy Part

These generate task.wait(1) and Part:Destroy().

## Modules

    import Inventory as Inv

Luau output:

    local Inv = require(script.Parent.Inventory)

## Error handling

TIRAN uses a common try/catch surface. Luau is translated through protected calls because Luau has no native try/catch syntax.

## Standard library

tiran_stdlib.py exposes BUILTINS, BUILTIN_COUNT, and get_builtin(name).
The registry contains exactly 11,000 callable names.
