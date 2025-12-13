import { PDFDocument } from 'pdf-lib';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const pdfDir = './Chapters_V4/PDF';
const outputDir = './MethodBook Complete';

// Ensure output directory exists
if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
}

const pdfFiles = [
    '00_Preface.pdf',
    '00_Introduction.pdf',
    '01_The_Mirror.pdf',
    '02_Crystal_Silence.pdf',
    '03_Orbit.pdf',
    '04_Parallax.pdf',
    '05_First_Light.pdf',
    '06_Angular_Motion.pdf',
    '07_Blue_Cycle.pdf',
    '08_Harmolodic_Sketch.pdf',
    '09_Entangled_Horizons.pdf',
    '10_Fractured_Light.pdf',
    '11_Greezy.pdf'
];

async function mergePDFs() {
    const mergedPdf = await PDFDocument.create();
    
    // Set metadata
    mergedPdf.setTitle('GCE Jazz - Trio Tunes Method Book V4');
    mergedPdf.setAuthor('Mike Bryant');
    mergedPdf.setSubject('Jazz Guitar Method Book - 11 Original Compositions');
    mergedPdf.setCreator('GCE Jazz');
    mergedPdf.setCreationDate(new Date());
    
    for (const pdfFile of pdfFiles) {
        const pdfPath = join(pdfDir, pdfFile);
        console.log(`Adding: ${pdfFile}`);
        
        try {
            const pdfBytes = readFileSync(pdfPath);
            const pdf = await PDFDocument.load(pdfBytes);
            const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
            copiedPages.forEach((page) => mergedPdf.addPage(page));
        } catch (err) {
            console.error(`Error loading ${pdfFile}:`, err.message);
        }
    }
    
    const mergedPdfBytes = await mergedPdf.save();
    const outputPath = join(outputDir, 'V4_MethodBook_Complete.pdf');
    writeFileSync(outputPath, mergedPdfBytes);
    
    console.log(`\n✓ Created: ${outputPath}`);
    console.log(`✓ Total pages: ${mergedPdf.getPageCount()}`);
    console.log(`✓ File size: ${(mergedPdfBytes.length / 1024 / 1024).toFixed(2)} MB`);
}

mergePDFs().catch(console.error);

