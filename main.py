import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from PIL import Image, ImageTk
import io
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

class CurrencyConverter:
    def __init__(self):
        self.api_key = "6c99af28bd98e25867824720"
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/KRW"
        self.rates = self.get_exchange_rates()

    def get_exchange_rates(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            data = response.json()
            return data['conversion_rates']
        except requests.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return {}
        except (KeyError, ValueError) as e:
            print(f"응답 데이터 처리 중 오류 발생: {e}")
            return {}

    def convert(self, amount, from_currency, to_currency):
        if self.rates:
            krw_amount = amount / self.rates[from_currency]
            return krw_amount * self.rates[to_currency]
        return None

class CurrencyConverterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("환율 계산기")
        self.master.geometry("800x600")
        self.converter = CurrencyConverter()
    
    @app.route('/')
    def index():
        return render_template('index.html', rates=converter.rates)

        if not self.converter.rates:
            messagebox.showerror("오류", "환율 정보를 불러오는 데 실패했습니다.\n인터넷 연결을 확인하고 프로그램을 다시 실행해주세요.")
        
        self.create_widgets()

    def create_widgets(self):
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(1, weight=1)

        self.create_header()
        self.create_rates_frame()
        self.create_converter_frame()

    def create_header(self):
        header_frame = ttk.Frame(self.master, padding="20 20 20 0")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        title_label = ttk.Label(header_frame, text="환율 계산기", font=("Helvetica", 24, "bold"))
        title_label.pack()

        self.add_logo(header_frame)

    def add_logo(self, parent):
        try:
            url = ""  # 실제 이미지 URL로 교체하세요
            response = requests.get(url)
            response.raise_for_status()  # HTTP 오류 발생 시 예외를 발생시킵니다
            img_data = response.content
            print(f"Downloaded {len(img_data)} bytes")  # 다운로드된 데이터 크기 출력
            
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((50, 50), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            logo_label = ttk.Label(parent, image=photo)
            logo_label.image = photo
            logo_label.pack(side="left", padx=(0, 20))
        except requests.RequestException as e:
            print(f"Error downloading image: {e}")
        except PIL.UnidentifiedImageError as e:
            print(f"Error opening image: {e}")
            print(f"First 100 bytes of data: {img_data[:100]}")  # 다운로드된 데이터의 시작 부분 출력
        except Exception as e:
            print(f"Unexpected error: {e}")

    def create_rates_frame(self):
        rates_frame = ttk.Frame(self.master, padding="20")
        rates_frame.grid(row=1, column=0, sticky="nsew")

        ttk.Label(rates_frame, text="환율 정보", font=("Helvetica", 18, "bold")).pack(pady=(0, 10))

        rates_text = tk.Text(rates_frame, wrap=tk.WORD, width=30, height=20)
        rates_text.pack(fill=BOTH, expand=YES)

        if self.converter.rates:
            rates_text.insert(tk.END, "기준 통화: 1 KRW\n\n")
            for currency, rate in self.converter.rates.items():
                rates_text.insert(tk.END, f"{currency}: {1/rate:.6f} KRW\n")
        else:
            rates_text.insert(tk.END, "환율 정보를 불러오는 데 실패했습니다.\n")
            rates_text.insert(tk.END, "인터넷 연결을 확인하고 다시 시도해주세요.")

        rates_text.config(state=tk.DISABLED)

    def create_converter_frame(self):
        converter_frame = ttk.Frame(self.master, padding="20")
        converter_frame.grid(row=1, column=1, sticky="nsew")

        ttk.Label(converter_frame, text="환율 변환", font=("Helvetica", 18, "bold")).pack(pady=(0, 20))

        amount_frame = ttk.Frame(converter_frame)
        amount_frame.pack(fill=X, pady=5)
        ttk.Label(amount_frame, text="금액:").pack(side=LEFT)
        self.amount_entry = ttk.Entry(amount_frame)
        self.amount_entry.pack(side=LEFT, expand=YES, fill=X, padx=(10, 0))

        from_frame = ttk.Frame(converter_frame)
        from_frame.pack(fill=X, pady=5)
        ttk.Label(from_frame, text="변환 전:").pack(side=LEFT)
        self.from_currency = ttk.Combobox(from_frame, values=list(self.converter.rates.keys()), state="readonly")
        self.from_currency.pack(side=LEFT, expand=YES, fill=X, padx=(10, 0))
        self.from_currency.set('KRW')

        to_frame = ttk.Frame(converter_frame)
        to_frame.pack(fill=X, pady=5)
        ttk.Label(to_frame, text="변환 후:").pack(side=LEFT)
        self.to_currency = ttk.Combobox(to_frame, values=list(self.converter.rates.keys()), state="readonly")
        self.to_currency.pack(side=LEFT, expand=YES, fill=X, padx=(10, 0))
        self.to_currency.set('USD')

        ttk.Button(converter_frame, text="변환", command=self.convert, style='Accent.TButton').pack(pady=20)

        self.result_label = ttk.Label(converter_frame, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=10)

    @app.route('/convert', methods=['POST'])
    def convert():
        amount = float(request.form['amount'])
        from_curr = request.form['from_currency']
        to_curr = request.form['to_currency']
        result = converter.convert(amount, from_curr, to_curr)
        return jsonify({'result': f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    app = CurrencyConverterApp(root)
    root.mainloop()