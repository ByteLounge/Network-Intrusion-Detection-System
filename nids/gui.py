import threading
import traceback
from pathlib import Path
import sys

# Ensure project root is on sys.path so `import nids.*` works when running this file directly
PROJ_ROOT = Path(__file__).resolve().parents[1]
proj_root_str = str(PROJ_ROOT)
if proj_root_str not in sys.path:
    sys.path.insert(0, proj_root_str)
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

ROOT = Path(__file__).parent

def run_in_thread(target, args=()):
    def runner():
        try:
            target(*args)
        except Exception as e:
            txt.insert(tk.END, f"Error: {e}\n" + traceback.format_exc() + "\n")
        finally:
            btn_run.config(state=tk.NORMAL)
    btn_run.config(state=tk.DISABLED)
    threading.Thread(target=runner, daemon=True).start()

# action wrappers
def do_preprocess():
    inp = entry_input.get().strip()
    out = entry_output.get().strip()
    if not inp or not out:
        messagebox.showwarning('Missing', 'Please set input and output paths')
        return
    def work():
        txt.insert(tk.END, f'Running preprocess: {inp} -> {out}\n')
        from nids.ml.preprocess import load_and_prepare
        df = load_and_prepare(inp)
        df.to_csv(out, index=False)
        txt.insert(tk.END, 'Preprocess complete\n')
    run_in_thread(work)

def do_train():
    data = entry_data.get().strip()
    out = entry_model.get().strip()
    if not data or not out:
        messagebox.showwarning('Missing', 'Please set training data and model output')
        return
    def work():
        txt.insert(tk.END, f'Training model from {data} -> {out}\n')
        from nids.ml.train_model import train
        train(data, out)
        txt.insert(tk.END, 'Training finished\n')
    run_in_thread(work)

def do_evaluate():
    data = entry_eval_data.get().strip()
    model = entry_eval_model.get().strip()
    if not data or not model:
        messagebox.showwarning('Missing', 'Please set evaluation data and model')
        return
    def work():
        txt.insert(tk.END, f'Evaluating {model} on {data}\n')
        from nids.ml.evaluate_model import evaluate
        evaluate(data, model)
        txt.insert(tk.END, 'Evaluation finished\n')
    run_in_thread(work)

def do_detect():
    csv = entry_detect_csv.get().strip()
    model = entry_detect_model.get().strip()
    if not csv or not model:
        messagebox.showwarning('Missing', 'Please set CSV and model')
        return
    def work():
        txt.insert(tk.END, f'Running detection: {csv} with {model}\n')
        from nids.detection.intrusion_detector import run_detection
        run_detection(csv, model)
        txt.insert(tk.END, 'Detection finished\n')
    run_in_thread(work)

def do_report():
    test = entry_report_test.get().strip()
    model = entry_report_model.get().strip()
    if not test or not model:
        messagebox.showwarning('Missing', 'Please set test CSV and model')
        return
    def work():
        txt.insert(tk.END, f'Generating report for {test} with {model}\n')
        from nids.ml.evaluate_report import run_report
        run_report(test, model)
        txt.insert(tk.END, 'Report generated in nids/ml/reports\n')
    run_in_thread(work)

# UI layout
root = tk.Tk()
root.title('NIDS - Basic UI')
root.geometry('800x640')
frm = ttk.Frame(root, padding=10)
frm.pack(fill=tk.BOTH, expand=True)

# Preprocess
lab = ttk.Label(frm, text='Preprocess (raw dataset -> processed CSV)')
lab.grid(column=0, row=0, sticky='w')
entry_input = ttk.Entry(frm, width=60)
entry_input.grid(column=0, row=1, sticky='w')
entry_input.insert(0, str(ROOT.parent / 'data' / 'raw' / 'KDDTrain+.txt'))
entry_output = ttk.Entry(frm, width=60)
entry_output.grid(column=1, row=1, sticky='w')
entry_output.insert(0, str(ROOT.parent / 'data' / 'processed' / 'nsl_kdd_train.csv'))
btn_pre = ttk.Button(frm, text='Preprocess', command=do_preprocess)
btn_pre.grid(column=2, row=1, padx=5)

# Train
ttk.Label(frm, text='Train (processed CSV -> model)').grid(column=0, row=2, sticky='w')
entry_data = ttk.Entry(frm, width=60)
entry_data.grid(column=0, row=3, sticky='w')
entry_data.insert(0, str(ROOT.parent / 'data' / 'processed' / 'nsl_kdd_train_binary.csv'))
entry_model = ttk.Entry(frm, width=60)
entry_model.grid(column=1, row=3, sticky='w')
entry_model.insert(0, str(ROOT / 'ml' / 'model_nsl_binary.pkl'))
btn_train = ttk.Button(frm, text='Train', command=do_train)
btn_train.grid(column=2, row=3, padx=5)

# Evaluate
ttk.Label(frm, text='Evaluate (test CSV -> model)').grid(column=0, row=4, sticky='w')
entry_eval_data = ttk.Entry(frm, width=60)
entry_eval_data.grid(column=0, row=5, sticky='w')
entry_eval_data.insert(0, str(ROOT.parent / 'data' / 'processed' / 'nsl_kdd_test_binary.csv'))
entry_eval_model = ttk.Entry(frm, width=60)
entry_eval_model.grid(column=1, row=5, sticky='w')
entry_eval_model.insert(0, str(ROOT / 'ml' / 'model_nsl_binary.pkl'))
btn_eval = ttk.Button(frm, text='Evaluate', command=do_evaluate)
btn_eval.grid(column=2, row=5, padx=5)

# Detect
ttk.Label(frm, text='Detect (CSV -> model)').grid(column=0, row=6, sticky='w')
entry_detect_csv = ttk.Entry(frm, width=60)
entry_detect_csv.grid(column=0, row=7, sticky='w')
entry_detect_csv.insert(0, str(ROOT.parent / 'data' / 'processed' / 'nsl_kdd_test.csv'))
entry_detect_model = ttk.Entry(frm, width=60)
entry_detect_model.grid(column=1, row=7, sticky='w')
entry_detect_model.insert(0, str(ROOT / 'ml' / 'model_nsl_fixed.pkl'))
btn_detect = ttk.Button(frm, text='Detect', command=do_detect)
btn_detect.grid(column=2, row=7, padx=5)

# Report
ttk.Label(frm, text='Report (test CSV -> model)').grid(column=0, row=8, sticky='w')
entry_report_test = ttk.Entry(frm, width=60)
entry_report_test.grid(column=0, row=9, sticky='w')
entry_report_test.insert(0, str(ROOT.parent / 'data' / 'processed' / 'nsl_kdd_test_binary.csv'))
entry_report_model = ttk.Entry(frm, width=60)
entry_report_model.grid(column=1, row=9, sticky='w')
entry_report_model.insert(0, str(ROOT / 'ml' / 'model_nsl_binary.pkl'))
btn_report = ttk.Button(frm, text='Report', command=do_report)
btn_report.grid(column=2, row=9, padx=5)

# Run/Log area
btn_run = ttk.Button(frm, text='Busy', state=tk.NORMAL)
btn_run.grid_forget()

txt = scrolledtext.ScrolledText(frm, wrap=tk.WORD, height=20)
txt.grid(column=0, row=10, columnspan=3, pady=10, sticky='nsew')
frm.rowconfigure(10, weight=1)
frm.columnconfigure(1, weight=1)

# Helpers: file pickers
def pick_input():
    p = filedialog.askopenfilename()
    if p:
        entry_input.delete(0, tk.END); entry_input.insert(0, p)

def pick_output():
    p = filedialog.asksaveasfilename(defaultextension='.csv')
    if p:
        entry_output.delete(0, tk.END); entry_output.insert(0, p)

# Quick buttons
ttk.Button(frm, text='Pick Input', command=pick_input).grid(column=3, row=1)
ttk.Button(frm, text='Pick Output', command=pick_output).grid(column=3, row=1, sticky='s')

if __name__ == '__main__':
    root.mainloop()
