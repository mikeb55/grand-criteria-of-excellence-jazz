import { PDFDocument, PDFName, PDFDict, PDFArray, PDFString, PDFNumber } from 'pdf-lib';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const pdfDir = './Chapters_V4/PDF';
const outputDir = './MethodBook Complete';

// Ensure output directory exists
if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
}

// Chapter definitions with titles for bookmarks
const chapters = [
    { file: '00_Preface.pdf', title: 'Preface' },
    { file: '00_Introduction.pdf', title: 'Introduction & Table of Contents' },
    { file: '01_The_Mirror.pdf', title: 'Chapter 1: The Mirror (Jim Hall)' },
    { file: '02_Crystal_Silence.pdf', title: 'Chapter 2: Crystal Silence (Chick Corea)' },
    { file: '03_Orbit.pdf', title: 'Chapter 3: Orbit (Wayne Shorter)' },
    { file: '04_Parallax.pdf', title: 'Chapter 4: Parallax (John Scofield)' },
    { file: '05_First_Light.pdf', title: 'Chapter 5: First Light (Pat Metheny)' },
    { file: '06_Angular_Motion.pdf', title: 'Chapter 6: Angular Motion (Pat Martino)' },
    { file: '07_Blue_Cycle.pdf', title: 'Chapter 7: Blue Cycle (Rosenwinkel/Monder)' },
    { file: '08_Harmolodic_Sketch.pdf', title: 'Chapter 8: Harmolodic Sketch (Bill Frisell)' },
    { file: '09_Entangled_Horizons.pdf', title: 'Chapter 9: Entangled Horizons (Ant Law)' },
    { file: '10_Fractured_Light.pdf', title: 'Chapter 10: Fractured Light (Ant Law)' },
    { file: '11_Greezy.pdf', title: 'Chapter 11: Greezy (Grant Green)' }
];

async function mergePDFs() {
    const mergedPdf = await PDFDocument.create();
    
    // Set metadata
    mergedPdf.setTitle('GCE Jazz - Trio Tunes Method Book V4');
    mergedPdf.setAuthor('Mike Bryant');
    mergedPdf.setSubject('Jazz Guitar Method Book - 11 Original Compositions');
    mergedPdf.setCreator('GCE Jazz');
    mergedPdf.setCreationDate(new Date());
    
    // Track page numbers for bookmarks
    const bookmarks = [];
    let currentPage = 0;
    
    for (const chapter of chapters) {
        const pdfPath = join(pdfDir, chapter.file);
        console.log(`Adding: ${chapter.file} (starts at page ${currentPage + 1})`);
        
        try {
            const pdfBytes = readFileSync(pdfPath);
            const pdf = await PDFDocument.load(pdfBytes);
            const pageCount = pdf.getPageCount();
            
            // Record bookmark info
            bookmarks.push({
                title: chapter.title,
                pageIndex: currentPage
            });
            
            const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
            copiedPages.forEach((page) => mergedPdf.addPage(page));
            
            currentPage += pageCount;
        } catch (err) {
            console.error(`Error loading ${chapter.file}:`, err.message);
        }
    }
    
    // Add PDF outline (bookmarks)
    console.log('\nAdding bookmarks...');
    const context = mergedPdf.context;
    const pages = mergedPdf.getPages();
    
    // Create outline items
    const outlineItems = [];
    
    for (let i = 0; i < bookmarks.length; i++) {
        const bookmark = bookmarks[i];
        const page = pages[bookmark.pageIndex];
        const pageRef = page.ref;
        
        // Create destination array [page /Fit]
        const destArray = context.obj([pageRef, PDFName.of('Fit')]);
        
        // Create outline item dictionary
        const outlineItem = context.obj({
            Title: PDFString.of(bookmark.title),
            Parent: null, // Will be set later
            Dest: destArray,
        });
        
        outlineItems.push(context.register(outlineItem));
    }
    
    // Link outline items (Prev/Next)
    for (let i = 0; i < outlineItems.length; i++) {
        const item = context.lookup(outlineItems[i]);
        if (i > 0) {
            item.set(PDFName.of('Prev'), outlineItems[i - 1]);
        }
        if (i < outlineItems.length - 1) {
            item.set(PDFName.of('Next'), outlineItems[i + 1]);
        }
    }
    
    // Create outline dictionary
    const outlineDict = context.obj({
        Type: PDFName.of('Outlines'),
        First: outlineItems[0],
        Last: outlineItems[outlineItems.length - 1],
        Count: PDFNumber.of(outlineItems.length),
    });
    const outlineRef = context.register(outlineDict);
    
    // Set parent for all items
    for (const itemRef of outlineItems) {
        const item = context.lookup(itemRef);
        item.set(PDFName.of('Parent'), outlineRef);
    }
    
    // Add outline to catalog
    const catalog = mergedPdf.catalog;
    catalog.set(PDFName.of('Outlines'), outlineRef);
    catalog.set(PDFName.of('PageMode'), PDFName.of('UseOutlines')); // Open with bookmarks visible
    
    const mergedPdfBytes = await mergedPdf.save();
    const outputPath = join(outputDir, 'V4_MethodBook_Complete.pdf');
    writeFileSync(outputPath, mergedPdfBytes);
    
    console.log(`\n✓ Created: ${outputPath}`);
    console.log(`✓ Total pages: ${mergedPdf.getPageCount()}`);
    console.log(`✓ Bookmarks: ${bookmarks.length}`);
    console.log(`✓ File size: ${(mergedPdfBytes.length / 1024 / 1024).toFixed(2)} MB`);
    
    console.log('\nBookmark structure:');
    bookmarks.forEach((b, i) => {
        console.log(`  ${i + 1}. ${b.title} → Page ${b.pageIndex + 1}`);
    });
}

mergePDFs().catch(console.error);
