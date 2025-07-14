import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import math

# --- 物理常量 ---
C_LIGHT = 299792458  # 真空光速 (m/s)

class WaveguideCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("硅光波导参数计算器")
        self.root.geometry("500x500") # 调整窗口大小

        # --- 变量定义 ---
        self.beta_var = tk.StringVar()
        self.neff_var = tk.StringVar()
        self.lambda_var = tk.StringVar()
        self.freq_var = tk.StringVar() # 新增：频率变量
        self.formula_var = tk.StringVar()
        
        # --- 防止实时换算时无限递归的标志 ---
        self._is_updating = False

        # --- 绑定变量的实时更新事件 ---
        self.lambda_var.trace_add("write", self.update_from_wavelength)
        self.freq_var.trace_add("write", self.update_from_frequency)

        # --- 界面布局 ---
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(expand=True, fill="both")
        frame.grid_columnconfigure(1, weight=1)

        title_label = tk.Label(frame, text="请输入任意两项参数", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # --- 输入行 ---
        self.create_entry_row(frame, "传播常数 (β) [rad/m]:", self.beta_var, 1)
        self.create_entry_row(frame, "有效折射率 (n_eff):", self.neff_var, 2)
        
        # --- 创建波长和频率的联动输入行 ---
        self.create_wavelength_freq_rows(frame, 3)

        # 公式显示
        formula_label = tk.Label(frame, textvariable=self.formula_var, font=("Arial", 13, "italic"), fg="#00008B")
        formula_label.grid(row=5, column=0, columnspan=3, pady=(15, 10))
        self.formula_var.set("计算公式将显示在此处")

        # 主操作按钮
        button_frame = tk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        calc_button = tk.Button(button_frame, text="计算", command=self.calculate, font=("Arial", 12), width=10)
        calc_button.pack(side=tk.LEFT, padx=10)
        clear_all_button = tk.Button(button_frame, text="全部清除", command=self.clear_all_fields, font=("Arial", 12), width=10)
        clear_all_button.pack(side=tk.LEFT, padx=10)

        # 历史记录框
        history_label = tk.Label(frame, text="历史记录:", font=("Arial", 12, "bold"))
        history_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(20, 5))
        self.history_text = scrolledtext.ScrolledText(frame, height=8, font=("Courier New", 10), state="disabled", wrap=tk.WORD)
        self.history_text.grid(row=8, column=0, columnspan=3, sticky="ew")

    def create_entry_row(self, parent, label_text, var, row):
        """创建独立的输入行 (β 和 n_eff)"""
        label = tk.Label(parent, text=label_text, font=("Arial", 12))
        label.grid(row=row, column=0, sticky="w", pady=5, padx=5)
        entry = tk.Entry(parent, textvariable=var, font=("Arial", 12))
        entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        clear_button = tk.Button(parent, text="X", command=lambda: var.set(""), font=("Arial", 10, "bold"), fg="red", width=2, height=1)
        clear_button.grid(row=row, column=2, sticky="w", padx=(0, 5))

    def create_wavelength_freq_rows(self, parent, start_row):
        """创建波长和频率的联动输入行"""
        # 波长行
        label_l = tk.Label(parent, text="波长 (λ) [nm]:", font=("Arial", 12))
        label_l.grid(row=start_row, column=0, sticky="w", pady=5, padx=5)
        entry_l = tk.Entry(parent, textvariable=self.lambda_var, font=("Arial", 12))
        entry_l.grid(row=start_row, column=1, sticky="ew", pady=5, padx=5)
        
        # 频率行
        label_f = tk.Label(parent, text="频率 (f) [THz]:", font=("Arial", 12))
        label_f.grid(row=start_row + 1, column=0, sticky="w", pady=5, padx=5)
        entry_f = tk.Entry(parent, textvariable=self.freq_var, font=("Arial", 12))
        entry_f.grid(row=start_row + 1, column=1, sticky="ew", pady=5, padx=5)

        # 统一的清除按钮
        clear_button = tk.Button(parent, text="X", command=self.clear_wavelength_frequency, font=("Arial", 10, "bold"), fg="red", width=2, height=1)
        # 将按钮放置在两行的中间
        clear_button.grid(row=start_row, column=2, sticky="w", padx=(0, 5), rowspan=2)

    def clear_wavelength_frequency(self):
        """同时清空波长和频率"""
        self.lambda_var.set("")
        self.freq_var.set("")
        
    def update_from_wavelength(self, *args):
        """当波长变化时，自动更新频率"""
        if self._is_updating: return
        self._is_updating = True
        try:
            lambda_nm = float(self.lambda_var.get())
            if lambda_nm > 0:
                lambda_m = lambda_nm * 1e-9
                freq_hz = C_LIGHT / lambda_m
                freq_thz = freq_hz / 1e12
                self.freq_var.set(f"{freq_thz:.2f}")
            else:
                self.freq_var.set("")
        except (ValueError, TypeError):
            self.freq_var.set("")
        self._is_updating = False

    def update_from_frequency(self, *args):
        """当频率变化时，自动更新波长"""
        if self._is_updating: return
        self._is_updating = True
        try:
            freq_thz = float(self.freq_var.get())
            if freq_thz > 0:
                freq_hz = freq_thz * 1e12
                lambda_m = C_LIGHT / freq_hz
                lambda_nm = lambda_m * 1e9
                self.lambda_var.set(f"{lambda_nm:.2f}")
            else:
                self.lambda_var.set("")
        except (ValueError, TypeError):
            self.lambda_var.set("")
        self._is_updating = False

    def clear_all_fields(self):
        """清除所有输入框和历史记录"""
        for var in [self.beta_var, self.neff_var, self.lambda_var, self.freq_var]:
            var.set("")
        self.formula_var.set("计算公式将显示在此处")
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state="disabled")

    def add_to_history(self, beta, neff, lambda_nm, freq_thz):
        """将结果添加到历史记录"""
        record = (f"β: {beta:<15s}n_eff: {neff:<9s}"
                  f"λ: {lambda_nm:<8s}f: {freq_thz:<8s}\n")
        self.history_text.config(state="normal")
        self.history_text.insert(tk.INSERT, record)
        self.history_text.config(state="disabled")

    def calculate(self):
        """核心计算函数"""
        try:
            # 优先使用波长，如果波长为空，则尝试从频率计算波长
            lambda_str = self.lambda_var.get()
            if not lambda_str:
                self.update_from_frequency() # 确保波长值由频率更新
                lambda_str = self.lambda_var.get()

            inputs = {
                'beta': float(self.beta_var.get()) if self.beta_var.get() else None,
                'neff': float(self.neff_var.get()) if self.neff_var.get() else None,
                'lambda_m': float(lambda_str) * 1e-9 if lambda_str else None
            }

            if list(inputs.values()).count(None) != 1:
                messagebox.showerror("输入错误", "请确保 β, n_eff, (λ/f) 三组参数中恰好填写了两组。")
                return

            if inputs['beta'] is None:
                neff, lambda_m = inputs['neff'], inputs['lambda_m']
                if lambda_m == 0: raise ValueError("波长不能为零。")
                beta_calc = neff * 2 * math.pi / lambda_m
                self.beta_var.set(f"{beta_calc:.2f}")
                self.formula_var.set("公式: β = n_eff * 2π / λ")

            elif inputs['neff'] is None:
                beta, lambda_m = inputs['beta'], inputs['lambda_m']
                neff_calc = beta * lambda_m / (2 * math.pi)
                self.neff_var.set(f"{neff_calc:.6f}")
                self.formula_var.set("公式: n_eff = (β * λ) / 2π")

            elif inputs['lambda_m'] is None:
                beta, neff = inputs['beta'], inputs['neff']
                if beta == 0: raise ValueError("传播常数不能为零。")
                lambda_m_calc = neff * 2 * math.pi / beta
                self.lambda_var.set(f"{lambda_m_calc * 1e9:.2f}") # 这会自动触发频率更新
                self.formula_var.set("公式: λ = (n_eff * 2π) / β")
            
            # 计算成功后，同步更新另一项（以防万一）并记录
            self.update_from_wavelength()
            self.add_to_history(self.beta_var.get(), self.neff_var.get(), self.lambda_var.get(), self.freq_var.get())

        except (ValueError, TypeError):
            messagebox.showerror("输入错误", "请输入有效的数值。")
            self.formula_var.set("计算公式将显示在此处")
        except ZeroDivisionError:
            messagebox.showerror("计算错误", "输入值导致除以零，请检查输入。")
            self.formula_var.set("计算公式将显示在此处")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaveguideCalculatorApp(root)
    root.mainloop()
