# laya-rlcd-expedition

A small local page for work and sales decisions. It runs [Laya](https://huggingface.co/convaiinnovations/laya) on your machine through the official `laya` package. There is no API key and no cloud decision service.

Paste a note, pick a decision type, and the page shows the choice, confidence, option probabilities, the checkpoint that ran, and how long inference took.

## Install these first

A new computer needs the tools below before this project can run. Download them from the source sites, then install them.

| What | Why | Where to get it |
| --- | --- | --- |
| Git | Clone this repository | https://git-scm.com/downloads |
| Python 3.10 or newer | Run the app. 3.11 or 3.13 is fine. | https://www.python.org/downloads/ |

On Windows, during the Python install, turn on **Add python.exe to PATH**. If you skip that, use the `py` launcher shown below.

You also need a network connection the first time, and about 4 GB of free disk. PyTorch is large, and the English Laya checkpoint is about 800 MB.

## What the project downloads for you

You do not install these by hand. `pip` and the first server start fetch them.

| What | When | Source |
| --- | --- | --- |
| Flask | `pip install` | https://pypi.org/project/Flask/ |
| `laya` | `pip install` | https://pypi.org/project/laya/ |
| PyTorch, Transformers, Hugging Face Hub | pulled in by `laya` | https://pypi.org/project/torch/ and https://pypi.org/project/transformers/ |
| `convaiinnovations/laya` | first time the server loads the model | https://huggingface.co/convaiinnovations/laya |

`Router` picks the English checkpoint for English text. A note in another language can also download the multilingual checkpoint from the same Hugging Face repo.

## Setup

Clone the repo and enter the folder:

```bash
git clone https://github.com/HambaliMarcel/laya-rlcd-expedition.git
cd laya-rlcd-expedition
```

Create a virtual environment and install the Python packages.

Windows PowerShell, if `python` is on your PATH:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Windows, if only the Python launcher is available:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Run

Windows:

```powershell
.\.venv\Scripts\python.exe server.py
```

macOS or Linux:

```bash
.venv/bin/python server.py
```

Then open http://127.0.0.1:8000

The corner of the page says **Laya: Loading...** while the checkpoint downloads and loads. Wait until it says **Laya: Loaded**, then use **Analyze**. Later starts reuse the cached model and skip the download.

Leave that terminal open while you use the page. Stop the server with Ctrl+C.

## Decision types

| Dropdown | Choices |
| --- | --- |
| Task Priority | `DO_NOW`, `SCHEDULE`, `DELEGATE`, `IGNORE` |
| Sales Lead | `PURSUE`, `NURTURE`, `LOW_PRIORITY` |
| Proposal/Tender | `PURSUE`, `REVIEW`, `SKIP` |
| Project Risk | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
