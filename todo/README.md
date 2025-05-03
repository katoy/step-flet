# Todoアプリ

## アプリの実行

### uv

デスクトップアプリとして実行:

```
uv run flet run
```

ウェブアプリとして実行:

```
uv run flet run --web
```

### Poetry

`pyproject.toml`から依存関係をインストール:

```
poetry install
```

デスクトップアプリとして実行:

```
poetry run flet run
```

ウェブアプリとして実行:

```
poetry run flet run --web
```

アプリの実行に関する詳細は、[Fletドキュメント](https://flet.dev/docs/getting-started/)を参照してください。

## アプリのビルド

### Android

```
flet build apk -v
```

`.apk`または`.aab`のビルドと署名に関する詳細は、[Android Packaging Guide](https://flet.dev/docs/publish/android/)を参照してください。

### iOS

```
flet build ipa -v
```

`.ipa`のビルドと署名に関する詳細は、[iOS Packaging Guide](https://flet.dev/docs/publish/ios/)を参照してください。

### macOS

```
flet build macos -v
```

macOSパッケージのビルドに関する詳細は、[macOS Packaging Guide](https://flet.dev/docs/publish/macos/)を参照してください。

### Linux

```
flet build linux -v
```

Linuxパッケージのビルドに関する詳細は、[Linux Packaging Guide](https://flet.dev/docs/publish/linux/)を参照してください。

### Windows

```
flet build windows -v
```

Windowsパッケージのビルドに関する詳細は、[Windows Packaging Guide](https://flet.dev/docs/publish/windows/)を参照してください。

## テスト

### テストを実行するには:

```
python -m unittest tests/test_main.py
```

### テストカバレッジを計測するには:

```
pip install coverage
coverage run -m unittest tests/test_main.py
coverage report

HTML形式でカバレッジレポートを作成するには:

```
coverage html
```

`.coveragerc`ファイルを作成し、カバレッジ計測から`tests/test_main.py`を除外します。

```
[run]
omit =
    tests/*
```

### カバレッジデータを削除するには:

```
coverage erase
```

## 参考情報

*   [https://flet.dev/docs/tutorials/python-todo](https://flet.dev/docs/tutorials/python-todo) (FletでPython ToDoアプリを作成する)
