import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
import traceback
import ast
import threading
import time
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TilemapStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tilemap Studio - Thesis Edition v46 (Robust Loading)")
        self.geometry("1600x900")
        self.minsize(1000, 600)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.source_cv = None 
        self.render_pil = None 
        self.atlas_pil = None 
        self.video_cap = None
        self.is_video = False
        self.is_playing = False
        
        self.cached_process_func = None
        self.last_code_hash = ""
        
        self.dynamic_params = {} 
        self.dynamic_widgets = {}
        self.render_job = None
        self.resize_job = None
        self.active_entry = None

        # --- LEFT SPLIT VIEW ---
        self.main_paned = tk.PanedWindow(self, orient=tk.VERTICAL, bg="#101010", sashwidth=10, sashrelief="flat", showhandle=True, handlepad=10, handlesize=10)
        self.main_paned.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # --- PREVIEWS SPLIT ---
        self.preview_paned = tk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL, bg="#101010", sashwidth=10, sashrelief="flat", showhandle=True, handlepad=10, handlesize=10)
        self.main_paned.add(self.preview_paned, minsize=300, stretch="always")

        # Source
        self.frame_input = ctk.CTkFrame(self.preview_paned)
        self.preview_paned.add(self.frame_input, minsize=200, stretch="always")
        self.frame_input.grid_rowconfigure(1, weight=1) 
        self.frame_input.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.frame_input, text="SOURCE", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(5,0))
        self.canvas_source = tk.Canvas(self.frame_input, bg="#1a1a1a", highlightthickness=0)
        self.canvas_source.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Input Buttons
        btn_box = ctk.CTkFrame(self.frame_input, fg_color="transparent")
        btn_box.grid(row=2, column=0, pady=10)
        ctk.CTkButton(btn_box, text="Load Image", command=self.load_image, width=100, height=30).pack(side="left", padx=5)
        ctk.CTkButton(btn_box, text="Load Video/GIF", command=self.load_video, width=120, height=30, fg_color="#553333").pack(side="left", padx=5)

        # Result
        self.frame_output = ctk.CTkFrame(self.preview_paned)
        self.preview_paned.add(self.frame_output, minsize=200, stretch="always")
        self.frame_output.grid_rowconfigure(1, weight=1) 
        self.frame_output.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.frame_output, text="RESULT", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(5,0))
        self.canvas_result = tk.Canvas(self.frame_output, bg="#1a1a1a", highlightthickness=0)
        self.canvas_result.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Output Tools
        tools_box = ctk.CTkFrame(self.frame_output, fg_color="transparent")
        tools_box.grid(row=2, column=0, pady=10)
        
        self.btn_play = ctk.CTkButton(tools_box, text="▶ Play", command=self.toggle_play, width=80, height=30, fg_color="gray")
        self.btn_play.pack(side="left", padx=5)
        self.btn_play.pack_forget() 
        
        ctk.CTkButton(tools_box, text="Save Image", command=self.save_image, fg_color="green", width=100, height=30).pack(side="left", padx=5)
        self.btn_save_video = ctk.CTkButton(tools_box, text="Render Video", command=self.save_video, fg_color="#228822", width=100, height=30)
        self.btn_save_video.pack(side="left", padx=5)
        self.btn_save_video.pack_forget()

        # --- CODE EDITOR ---
        self.frame_code = ctk.CTkFrame(self.main_paned)
        self.main_paned.add(self.frame_code, minsize=150, stretch="always")
        top_bar = ctk.CTkFrame(self.frame_code, fg_color="transparent", height=30)
        top_bar.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(top_bar, text="LOGIC EDITOR", font=("Arial", 12, "bold")).pack(side="left")
        ctk.CTkButton(top_bar, text="↻ REFRESH UI", command=self.parse_and_build_ui, fg_color="#444", width=120, height=24).pack(side="right")
        self.txt_code = ctk.CTkTextbox(self.frame_code, font=("Consolas", 13), wrap="none")
        self.txt_code.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_code.insert("0.0", "") 

        # --- PARAMETERS ---
        self.frame_params = ctk.CTkFrame(self, width=320)
        self.frame_params.grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=10)
        self.frame_params.grid_propagate(False)
        self.btn_render = ctk.CTkButton(self.frame_params, text="FORCE REFRESH", command=self.force_update, height=40, font=("Arial", 12, "bold"), fg_color="#D97816")
        self.btn_render.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.frame_params, text="RESOURCES", font=("Arial", 12, "bold")).pack(pady=(10,5))
        self.btn_load_atlas = ctk.CTkButton(self.frame_params, text="Load Atlas Texture", command=self.load_atlas, fg_color="#555")
        self.btn_load_atlas.pack(pady=5)
        self.scroll_params = ctk.CTkScrollableFrame(self.frame_params, label_text="Parameters")
        self.scroll_params.pack(fill="both", expand=True, padx=10, pady=10)

        self.parse_and_build_ui()
        self.canvas_source.bind("<Configure>", self.on_resize)
        self.canvas_result.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.check_close_entry) 
        self.tk_source = None
        self.tk_result = None

    # --- ROBUST FILE LOADING ---
    def read_image_safe(self, path):
        # Solves the issue where cv2.imread fails on non-ASCII paths (e.g. "Maturski")
        try:
            stream = open(path, "rb")
            bytes = bytearray(stream.read())
            numpyarray = np.asarray(bytes, dtype=np.uint8)
            return cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        except:
            return None

    def load_image(self):
        # 1. HARD STOP VIDEO
        self.stop_video()
        self.is_video = False
        
        # 2. CLEAR PREVIOUS STATE VISUALLY
        self.source_cv = None
        self.canvas_source.delete("all")
        self.canvas_result.delete("all")
        self.btn_play.pack_forget()
        self.btn_save_video.pack_forget()
        self.update() # Force UI refresh immediately

        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp")])
        if path:
            # Use safe reader
            img = self.read_image_safe(path)
            if img is not None:
                # Remove alpha channel if present (Logic code expects BGR)
                if len(img.shape) == 3 and img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                elif len(img.shape) == 2: # Gray
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    
                self.source_cv = img
                self.run_processing()
            else:
                messagebox.showerror("Error", "Failed to load image. Path might contain invalid characters.")

    def load_video(self):
        self.stop_video()
        self.source_cv = None
        self.canvas_source.delete("all")
        self.canvas_result.delete("all")
        self.update()

        path = filedialog.askopenfilename(filetypes=[("Videos/GIFs", "*.mp4 *.avi *.mov *.mkv *.gif *.webp")])
        if path:
            self.video_cap = cv2.VideoCapture(path)
            if self.video_cap.isOpened():
                self.is_video = True
                ret, frame = self.video_cap.read()
                if ret:
                    self.source_cv = frame
                    self.btn_play.configure(text="▶ Play", fg_color="green")
                    self.btn_play.pack(side="left", padx=5)
                    self.btn_save_video.pack(side="left", padx=5)
                    self.run_processing()

    def toggle_play(self):
        if not self.is_video: return
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.configure(text="⏸ Pause", fg_color="red")
            self.video_loop()
        else:
            self.btn_play.configure(text="▶ Play", fg_color="green")

    def stop_video(self):
        self.is_playing = False
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None
        self.btn_play.pack_forget()
        self.btn_save_video.pack_forget()

    def video_loop(self):
        if not (self.is_video and self.is_playing and self.video_cap and self.video_cap.isOpened()):
            return 

        ret, frame = self.video_cap.read()
        if not ret:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_cap.read()
        
        if ret:
            self.source_cv = frame
            self.process_frame_cached()
            
        self.after(33, self.video_loop)

    def save_video(self):
        if not self.is_video or not self.video_cap: return
        
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if not path: return

        width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.video_cap.get(cv2.CAP_PROP_FPS) or 30.0
        
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.video_cap.read()
        if not ret: return
        
        self.compile_logic()
        res_pil = self.execute_logic(frame)
        out_w, out_h = res_pil.size
        
        if out_w % 2 != 0: out_w -= 1
        if out_h % 2 != 0: out_h -= 1
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(path, fourcc, fps, (out_w, out_h))
            if not out.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(path, fourcc, fps, (out_w, out_h))
        except:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(path, fourcc, fps, (out_w, out_h))
        
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        prog_win = ctk.CTkToplevel(self)
        prog_win.title("Rendering...")
        prog_win.geometry("300x120")
        lbl = ctk.CTkLabel(prog_win, text="Rendering Frame 0...")
        lbl.pack(pady=20)
        prog_bar = ctk.CTkProgressBar(prog_win, width=200)
        prog_bar.pack(pady=5)
        prog_bar.set(0)
        
        try:
            count = 0
            while True:
                ret, frame = self.video_cap.read()
                if not ret: break
                
                res_pil = self.execute_logic(frame)
                if res_pil.size != (out_w, out_h):
                    res_pil = res_pil.crop((0, 0, out_w, out_h))
                
                res_cv = cv2.cvtColor(np.array(res_pil), cv2.COLOR_RGB2BGR)
                out.write(res_cv)
                
                count += 1
                if count % 5 == 0:
                    lbl.configure(text=f"Frame {count} / {total_frames}")
                    if total_frames > 0: prog_bar.set(count / total_frames)
                    prog_win.update()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Render Failed: {str(e)}")
        finally:
            out.release()
            prog_win.destroy()
            messagebox.showinfo("Success", "Render Complete!")
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # --- EDITABLE SLIDER LOGIC ---
    def make_editable(self, widget, param_name, slider_widget, parent_frame):
        def open_entry(event):
            if self.active_entry: self.active_entry.destroy()
            entry = ctk.CTkEntry(parent_frame, width=80, height=25)
            entry.place(in_=widget, relx=0.5, rely=0.5, anchor="center")
            val = self.dynamic_params.get(param_name, 0)
            entry.insert(0, str(val))
            entry.focus_set()
            self.active_entry = entry

            def confirm(e=None):
                try:
                    txt = entry.get()
                    new_val = float(txt)
                    min_v, max_v = slider_widget.cget("from_"), slider_widget.cget("to")
                    new_val = max(min_v, min(new_val, max_v))
                    slider_widget.set(new_val)
                    self.on_param_change(param_name, new_val, "entry")
                except: pass
                entry.destroy()
                self.active_entry = None

            entry.bind("<Return>", confirm)
            entry.bind("<FocusOut>", confirm)

        widget.bind("<Double-Button-1>", open_entry)

    def check_close_entry(self, event):
        if self.active_entry and event.widget != self.active_entry:
            self.active_entry.destroy()
            self.active_entry = None

    # --- CORE FUNCTIONS ---
    def on_resize(self, event):
        if self.resize_job: self.after_cancel(self.resize_job)
        self.resize_job = self.after(100, self.refresh_previews)

    def refresh_previews(self):
        if self.source_cv is not None:
            self.draw_image_on_canvas(self.canvas_source, Image.fromarray(cv2.cvtColor(self.source_cv, cv2.COLOR_BGR2RGB)), "source")
        if self.render_pil is not None:
            self.draw_image_on_canvas(self.canvas_result, self.render_pil, "result")

    def draw_image_on_canvas(self, canvas, pil_img, target_name):
        c_w = canvas.winfo_width()
        c_h = canvas.winfo_height()
        if c_w < 50 or c_h < 50: return 
        w, h = pil_img.size
        ratio = min(c_w / w, c_h / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        if new_w <= 0 or new_h <= 0: return
        
        algo = Image.BILINEAR if self.is_playing else Image.LANCZOS
        resized = pil_img.resize((new_w, new_h), algo)
        
        tk_img = ImageTk.PhotoImage(resized)
        if target_name == "source": self.tk_source = tk_img
        else: self.tk_result = tk_img
        canvas.delete("all")
        canvas.create_image(c_w // 2, c_h // 2, image=tk_img, anchor="center")

    def load_atlas(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                self.atlas_pil = Image.open(path).convert("RGBA")
                self.btn_load_atlas.configure(fg_color="green", text="Atlas Loaded!")
                self.run_processing()
            except: messagebox.showerror("Error", "Failed to load atlas")

    def open_zoom_window(self):
        if self.render_pil is None: return
        top = ctk.CTkToplevel(self)
        top.title("Fullscreen")
        top.geometry("1200x900")
        w, h = self.render_pil.size
        sw, sh = top.winfo_screenwidth()-100, top.winfo_screenheight()-100
        r = min(sw/w, sh/h)
        new_w, new_h = int(w*r), int(h*r)
        ctk_img = ctk.CTkImage(self.render_pil, size=(new_w, new_h))
        ctk.CTkLabel(top, text="", image=ctk_img).pack(expand=True, fill="both")

    def parse_and_build_ui(self):
        if self.active_entry: self.active_entry.destroy()
        self.active_entry = None
        code = self.txt_code.get("0.0", "end").strip()
        new_vars = {}
        sections = [] 
        if code:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith("# ---") and line.strip().endswith("---"):
                    name = line.strip().replace("# ---", "").replace("---", "").strip()
                    sections.append((i, name))
            try:
                tree = ast.parse(code)
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                          for t in node.targets:
                              if isinstance(t, ast.Name) and t.id.isupper():
                                  try: 
                                      val = ast.literal_eval(node.value)
                                      new_vars[t.id] = {'val': val, 'lineno': node.lineno}
                                  except: pass
            except: pass

        for w in self.scroll_params.winfo_children(): w.destroy()
        self.dynamic_widgets = {}
        sorted_vars = sorted(new_vars.items(), key=lambda x: x[1]['lineno'])
        current_section_idx = 0
        
        for name, data in sorted_vars:
            val = data['val']
            lineno = data['lineno']
            while current_section_idx < len(sections) and lineno > sections[current_section_idx][0]:
                sec_name = sections[current_section_idx][1]
                sep = ctk.CTkLabel(self.scroll_params, text=sec_name, fg_color="#333", corner_radius=6, height=24)
                sep.pack(fill="x", pady=(15, 5))
                current_section_idx += 1

            container = ctk.CTkFrame(self.scroll_params, fg_color="transparent")
            container.pack(fill="x", pady=2)
            ctk.CTkLabel(container, text=name, font=("Arial", 11, "bold")).pack(anchor="w")
            
            if isinstance(val, list):
                default_val = val[0]
                widget = ctk.CTkOptionMenu(container, values=val, command=lambda v, n=name: self.on_param_change(n, v, "menu"))
                widget.set(default_val)
                widget.pack(fill="x")
                self.dynamic_params[name] = default_val
                self.dynamic_widgets[name] = {'type': 'menu', 'container': container}

            elif isinstance(val, tuple) and len(val) == 3 and isinstance(val[0], int) and val[1]==0 and val[2]==1:
                chk_var = ctk.IntVar(value=val[0])
                widget = ctk.CTkCheckBox(container, text="Enable", variable=chk_var, command=lambda n=name, v=chk_var: self.on_param_change(n, v.get(), "check"))
                widget.pack(anchor="w")
                self.dynamic_params[name] = val[0]
                self.dynamic_widgets[name] = {'type': 'check', 'container': container}

            elif isinstance(val, tuple) and len(val) == 3:
                s_val, min_v, max_v = val
                slider = ctk.CTkSlider(container, from_=min_v, to=max_v, command=lambda v, n=name: self.on_param_change(n, v, "slider"))
                slider.set(s_val)
                slider.pack(fill="x")
                
                # PERMANENT ENTRY BOX
                entry = ctk.CTkEntry(container, width=80, height=24)
                entry.pack(pady=(2,0))
                entry.insert(0, str(s_val))
                
                def on_entry_commit(event, n=name, s=slider, e=entry):
                    try:
                        new_v = float(e.get())
                        mn, mx = s.cget("from_"), s.cget("to")
                        new_v = max(mn, min(new_v, mx))
                        s.set(new_v)
                        self.on_param_change(n, new_v, "entry")
                    except: pass
                    self.focus_set()

                entry.bind("<Return>", on_entry_commit)
                entry.bind("<FocusOut>", on_entry_commit)

                self.dynamic_widgets[name] = {'type': 'slider', 'entry': entry, 'slider': slider, 'container': container}
                self.dynamic_params[name] = s_val
            
            if name not in self.dynamic_widgets:
                self.dynamic_widgets[name] = {'type': 'other', 'container': container}
        
        self.check_visibility()

    def check_visibility(self):
        preset = self.dynamic_params.get("COLOR_PRESET", "")
        is_custom = (preset == "Custom")
        for name, widget_data in self.dynamic_widgets.items():
            if name.startswith("CUSTOM_"):
                if is_custom: widget_data['container'].pack(fill="x", pady=2)
                else: widget_data['container'].pack_forget()

    def on_param_change(self, name, val, source):
        self.dynamic_params[name] = val
        if source == "slider":
            info = self.dynamic_widgets.get(name)
            if info and 'entry' in info:
                current_entry = info['entry'].get()
                try:
                    if isinstance(val, int) or val.is_integer(): txt_val = str(int(val))
                    else: txt_val = f"{val:.2f}"
                    if current_entry != txt_val:
                        info['entry'].delete(0, "end")
                        info['entry'].insert(0, txt_val)
                except: pass

        if name == "COLOR_PRESET": self.check_visibility()
        if not self.is_playing:
            if self.render_job: self.after_cancel(self.render_job)
            self.render_job = self.after(50, self.run_processing)

    def compile_logic(self):
        code = self.txt_code.get("0.0", "end").strip()
        if not code: return False
        current_hash = str(hash(code))
        if self.cached_process_func and current_hash == self.last_code_hash:
            return True
        try:
            tree = ast.parse(code)
            new_body = [n for n in tree.body if not (isinstance(n, ast.Assign) and n.targets[0].id in self.dynamic_params)]
            tree.body = new_body
            exec_globals = self.dynamic_params.copy()
            exec(compile(tree, "<string>", "exec"), exec_globals)
            if 'process' in exec_globals:
                self.cached_process_func = exec_globals['process']
                self.last_code_hash = current_hash
                return True
        except Exception as e:
            traceback.print_exc()
            return False
        return False

    def execute_logic(self, frame):
        if self.cached_process_func:
            return self.cached_process_func(frame, self.atlas_pil, self.dynamic_params)
        return None

    def process_frame_cached(self):
        if self.source_cv is None: return
        res = self.execute_logic(self.source_cv)
        if res:
            self.render_pil = res
            self.refresh_previews()

    def run_processing(self):
        self.compile_logic()
        self.process_frame_cached()

    def force_update(self):
        self.last_code_hash = "" 
        self.run_processing()

    def save_image(self):
        if self.render_pil:
            path = filedialog.asksaveasfilename(defaultextension=".png")
            if path: self.render_pil.save(path)

if __name__ == "__main__":
    app = TilemapStudio()
    app.mainloop()
