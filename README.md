# Flappy Bird Game

A modern implementation of the classic Flappy Bird game with online leaderboards for Windows.

## Download and Installation

1. Download `FlappyBirdSetup.exe` from the [latest release](../../releases/latest)
2. Run the installer
3. Launch the game from the Start Menu or Desktop shortcut

## System Requirements
- Windows 10 or Windows 11
- 2GB RAM minimum
- 500MB disk space
- Internet connection for online leaderboard (optional)

## Features
- Classic Flappy Bird gameplay
- Online leaderboard system
- Modern graphics and sound effects
- Easy-to-use installer
- Automatic updates check

## Troubleshooting

### Missing Files or Dependencies
If you see errors about missing files:
1. Verify that the game was installed correctly
2. Try reinstalling the game
3. Check that your antivirus isn't blocking any files

### Audio Issues
- Ensure your system's audio is working
- Try updating your audio drivers
- The game will continue to work without audio files

### Online Features
- Internet connection required for leaderboard
- Game works offline, but scores won't be uploaded
- Check your firewall if you can't connect

## Development

### Building from Source
1. Clone the repository
2. Install Python 3.11+
3. Install dependencies: `pip install -r requirements.txt`
4. Run the game: `python game.py`

### Creating a Release
1. Tag your commit: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. GitHub Actions will automatically build and create the Windows installer

## Support
- Open an issue for bug reports
- Check existing issues for known problems
- Contact support for urgent issues

## License
This project is licensed under the MIT License - see the LICENSE file for details.
