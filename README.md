# Photo-Storage-Manager

# 1. Scan files, compute sha256, and record the info of files.

```
uv run .\main.py <your-first-directory>

uv run .\main.py F:\Robin合影
```

<img width="1109" height="402" alt="image" src="https://github.com/user-attachments/assets/c655d8e0-860f-4918-8702-0da3f31e6eee" />

.

## Incremental processing:

```
uv run .\main.py <your-next-directory>

uv run .\main.py F:\Robin合影
```
<img width="1136" height="384" alt="image" src="https://github.com/user-attachments/assets/2fef76ab-4367-4114-b9aa-27066e51494a" />


# 2. Copy and archiving the files incrementally

```
uv run .\main.py
```

<img width="713" height="314" alt="image" src="https://github.com/user-attachments/assets/34ce3244-5933-4191-a4e7-777b73b1f6c3" />
