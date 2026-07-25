use tauri_plugin_shell::ShellExt;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let sidecar = app.shell().sidecar("tienda-api")?;
            let (_rx, _child) = sidecar.spawn()?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running Tauri app");
}
