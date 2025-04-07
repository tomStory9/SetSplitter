<p align="center">
  <a href="https://github.com/Centre-National-des-arts-du-cirque/IntraCnac" target="_blank">
    <img src="public/TBG.png" width="40%" height ="40%" alt="TBG"/>
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/contributors/tomStory9/SetSplitter" alt="GitHub contributors"/>
  <img src="https://img.shields.io/github/discussions/tomStory9/SetSplitter" alt="GitHub discussions"/>
  <img src="https://img.shields.io/github/issues/tomStory9/SetSplitter" alt="GitHub issues"/>
  <img src="https://img.shields.io/github/issues-pr/tomStory9/SetSplitter" alt="GitHub pull requests"/>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python version"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status"/>
</p>

## 🗂️ Table of Contents

- [🗂️ Table of Contents](#️-table-of-contents)
- [📋 About](#-about)
- [🛠️ Tech Stack](#️-tech-stack)
  - [Core Components](#core-components)
- [📁 Project Structure](#-project-structure)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
- [👥 Contributors](#-contributors)
- [📜 License](#-license)

## 📋 About

Video Splitter is a Python utility that allows you to split a video into multiple segments based on timecodes defined in a CSV file. Perfect for extracting specific scenes, creating compilations, or preparing video sets for editing.

## 🛠️ Tech Stack

<table>
  <tr>
    <td align="center" width="96">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="48" height="48" alt="Python" />
      <br>Python
    </td>
    <td align="center" width="96">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pandas/pandas-original.svg" width="48" height="48" alt="Pandas" />
      <br>Pandas
    </td>
    <td align="center" width="96">
      <img src="https://zulko.github.io/moviepy/_static/logo_small.jpeg" width="48" height="48" alt="MoviePy" />
      <br>MoviePy
    </td>
  </tr>
</table>

### Core Components
- 🎬 MoviePy for video processing
- 📊 Pandas for CSV handling
- ⏱️ Built-in time conversion utilities
- 🎯 Command-line interface

## 📁 Project Structure

```
VideoSplitter/
├── main.py            # Main application script
├── requirements.txt   # Python dependencies
├── public/            # Public assets
└── sets_output/       # Output directory (auto-created)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/video-splitter
   cd video-splitter
   ```

2. **Create and Activate Virtual Environment**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate on Windows
   venv\Scripts\activate

   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. **Prepare a CSV file** with the following columns:
   - `set_name`: Name for the output file
   - `start1`, `end1`, `start2`, `end2`, etc.: Timecodes in HH:MM:SS format

2. **Run the script**:

   ```bash
   python main.py path/to/video.mp4 path/to/timecodes.csv
   ```

3. **Find your split videos** in the `sets_output` directory


## 👥 Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/tomStory9">
        <img src="https://avatars.githubusercontent.com/u/97254191?v=4" width="100px;" alt="tomStory9"/>
        <br/>
        <sub><b>tomStory9</b></sub>
      </a>
    </td>
  </tr>
</table>

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <sub>Built with ❤️ For TheBattleGround</sub>
</div>