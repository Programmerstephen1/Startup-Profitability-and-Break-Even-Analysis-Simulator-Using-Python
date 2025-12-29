Applying and committing the project locally

Files:
- startup_simulator.zip : full project archive (contains all files and directories)

Instructions to unpack and create a local git repo:

1. Unzip the archive into a folder and change into it:

```powershell
Expand-Archive -Path startup_simulator.zip -DestinationPath ./StartupSimulator
cd .\StartupSimulator
```

2. Initialize git, add files, and create the first commit:

```bash
git init
git add .
git commit -m "Initial simulator scaffold: core, CLI, plotting, tests, sample config, web UI"
```

3. (Optional) Create a remote and push:

```bash
git branch -M main
git remote add origin <your-remote-repo-url>
git push -u origin main
```

If you prefer to apply a patch file instead of a ZIP, let me know and I will generate a unified diff you can apply with `git apply` or `patch`.
