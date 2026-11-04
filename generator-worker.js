import { loadPyodide } from 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs';

async function setup() {
    // Start Python and install the schematic dependencies once
    const python = await loadPyodide();
    await python.loadPackage(['numpy', 'micropip']);
    await python.runPythonAsync(`
import micropip
await micropip.install("litemapy==0.11.0b0")
    `);

    // Copy the template into Python's temporary filesystem
    const templateName = 'Brittle ice Spleef Arena by JimberryDev.litematic';
    const template = await fetch(`./${templateName}`);
    if (!template.ok) throw new Error('Could not load the template');
    python.FS.writeFile(
        templateName,
        new Uint8Array(await template.arrayBuffer())
    );

    // Import the generator without running its local __main__ example
    const source = await fetch('./generator.py');
    if (!source.ok) throw new Error('Could not load generator.py');
    python.FS.writeFile('generator.py', await source.text());
    await python.runPythonAsync('import generator');

    return python;
}

let python;

async function start() {
    // Tell the page when Python is ready, or why loading failed
    try {
        python = await setup();
        self.postMessage({ type: 'ready' });
    } catch (error) {
        self.postMessage({ type: 'error', message: String(error) });
    }
}

self.onmessage = async ({ data }) => {
    if (!python) return;

    try {
        // Pass tile counts as variables rather than inserting them into code
        python.globals.set('width_tiles', data.widthTiles);
        python.globals.set('height_layers', data.heightLayers);
        python.globals.set('length_tiles', data.lengthTiles);

        const path = await python.runPythonAsync(`
generator.gen_schem(width_tiles, height_layers, length_tiles)
        `);

        // Read the output bytes and remove the temporary generated file
        const bytes = python.FS.readFile(path);
        python.FS.unlink(path);

        // Send the file back so the page can offer a download
        self.postMessage({
            type: 'complete',
            bytes,
            filename: path.split('/').pop(),
        });
    } catch (error) {
        self.postMessage({ type: 'error', message: String(error) });
    }
};

// Register the message handler before starting Python
start();
