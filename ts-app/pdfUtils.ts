// Funcții pentru generarea PDF-ului cu pdf-lib
import { PDFDocument, rgb } from 'pdf-lib';
import { Equipment } from './types';

// Exemplu de funcție pentru generarea unui PDF simplu
export async function generateInspectionPDF(
  eq: Equipment,
  answers: string[],
  comments: string[],
  otherComment: string,
  discard: string,
  discardReason: string,
  disposalAction: string
): Promise<Uint8Array> {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([595, 842]); // A4

  page.drawText('Små-materiel eftersynsrapport', { x: 50, y: 800, size: 18 });
  page.drawText(`Firma: ${eq.firma}`, { x: 50, y: 780, size: 12 });
  page.drawText(`Maskin nr: ${eq.maskin_nr}`, { x: 50, y: 765, size: 12 });
  // ... alte câmpuri ...

  // Exemplu: listă de verificare
  answers.forEach((ans, idx) => {
    page.drawText(`${idx + 1}. ${ans} - ${comments[idx] || ''}`, { x: 50, y: 740 - idx * 18, size: 11 });
  });

  // Alte comentarii
  page.drawText(`Alte comentarii: ${otherComment}`, { x: 50, y: 520, size: 11 });

  // Discard info
  page.drawText(`Kassering: ${discard}`, { x: 50, y: 500, size: 11 });
  if (discard === 'Ja') {
    page.drawText(`Motiv: ${discardReason}`, { x: 50, y: 485, size: 11 });
    page.drawText(`Håndtering: ${disposalAction}`, { x: 50, y: 470, size: 11 });
  }

  return await pdfDoc.save();
}
