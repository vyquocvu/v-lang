# Cài đặt VS Code / VS Code Setup

Hướng dẫn cài đặt môi trường lập trình v-lang trong Visual Studio Code.

---

## 1. Cài đặt Extension (planned)

!!! note "Đang phát triển"
    VS Code extension chưa được phát hành. Hướng dẫn này mô tả cách cài đặt thủ công.

### Cài đặt thủ công / Manual Setup

Trong khi extension chưa có trên marketplace, bạn có thể cài thủ công:

```bash
git clone https://github.com/vyquocvu/vscode-vlang.git
cd vscode-vlang
npm install
code --install-extension vlang-*.vsix
```

---

## 2. Nhận dạng file `.vpl` / File Association

Thêm vào VS Code `settings.json`:

```json
{
  "files.associations": {
    "*.vpl": "vlang"
  }
}
```

---

## 3. Task Runner

Thêm `.vscode/tasks.json` vào project của bạn:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "vlang: Compile",
      "type": "shell",
      "command": "vlang compile ${file} -o ${fileBasenameNoExtension}",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": []
    },
    {
      "label": "vlang: Run",
      "type": "shell",
      "command": "./${fileBasenameNoExtension}",
      "dependsOn": "vlang: Compile",
      "group": {
        "kind": "test",
        "isDefault": true
      }
    }
  ]
}
```

Phím tắt: `Ctrl+Shift+B` (hoặc `Cmd+Shift+B` trên macOS) để biên dịch.

---

## 4. Cú pháp nổi bật / Syntax Highlighting

Tạm thời dùng highlighting của Ruby (cú pháp tương tự):

```json
{
  "files.associations": {
    "*.vpl": "ruby"
  }
}
```

---

## 5. Language Server (planned)

Khi `vlang lsp` được phát triển, thêm vào `settings.json`:

```json
{
  "vlang.lsp.enabled": true,
  "vlang.lsp.path": "vlang"
}
```

---

## Editors khác / Other Editors

| Editor | Hỗ trợ | Hướng dẫn |
|---|---|---|
| VS Code | 🔄 Đang phát triển | Trang này |
| Neovim | 📋 Kế hoạch | LSP client + treesitter grammar |
| Emacs | 📋 Kế hoạch | lsp-mode integration |
| JetBrains | 📋 Kế hoạch | IntelliJ plugin |
