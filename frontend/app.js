// ==========================================
// ส่วนที่ 1: การตั้งค่า (CONFIG) - ห้ามลบ
// ==========================================
const API_BASE = "https://taxproject-vaum.onrender.com";
const subCategoriesByMain = {
    personal: [
        { value: "อุปการะเลี้ยงดูบิดามารดา", label: "อุปการะเลี้ยงดูบิดามารดา" },
        { value: "เบี้ยประกันสุขภาพบิดามารดา", label: "เบี้ยประกันสุขภาพบิดามารดา" },
        { value: "อุปการะเลี้ยงดูคนพิการหรือคนทุพพลภาพ", label: "อุปการะเลี้ยงดูคนพิการหรือคนทุพพลภาพ" }
    ],
    investment: [
        { value: "เบี้ยประกันชีวิต", label: "เบี้ยประกันชีวิต" },
        { value: "เบี้ยประกันสุขภาพ", label: "เบี้ยประกันสุขภาพ" },
        { value: "เบี้ยประกันชีวิตแบบบำนาญ", label:"เบี้ยประกันชีวิตแบบบำนาญ"},
        { value: "เงินสะสมกองทุนสำรองเลี้ยงชีพ", label: "เงินสะสมกองทุนสำรองเลี้ยงชีพ" },
        { value: "เงินสะสมกองทุนบำเหน็จบำนาญ (กบข.)", label: "เงินสะสมกองทุนบำเหน็จบำนาญ (กบข.)" },
        { value: "เงินสะสมกองทุนสงเคราะห์ครูโรงเรียนเอกชน", label: "เงินสะสมกองทุนสงเคราะห์ครูโรงเรียนเอกชน" },
        { value: "เงินค่าชดเชยที่ได้รับตามกฎหมายแรงงาน (กรณีนำมารวมคำนวณภาษี)", label:"เงินค่าชดเชยที่ได้รับตามกฎหมายแรงงาน (กรณีนำมารวมคำนวณภาษี)"},
        { value: "เงินสะสมกองทุนการออมแห่งชาติ (กอช.)", label: "เงินสะสมกองทุนการออมแห่งชาติ (กอช.)" },
        { value: "ค่าซื้อหน่วยลงทุนในกองทุนรวมเพื่อการออม SSF", label: "ค่าซื้อหน่วยลงทุนในกองทุนรวมเพื่อการออม SSF" },
        { value: "ค่าซื้อหน่วยลงทุนเพื่อการเลี้ยงชีพ (RMF)", label: "ค่าซื้อหน่วยลงทุนเพื่อการเลี้ยงชีพ (RMF)" },
        { value: "เงินสมทบกองทุนประกันสังคม", label: "เงินสมทบกองทุนประกันสังคม" },
        { value: "ค่าซื้อหน่วยลงทุนในกองทุนรวมไทยเพื่อความยั่งยืน (Thai ESG)", label:"ค่าซื้อหน่วยลงทุนในกองทุนรวมไทยเพื่อความยั่งยืน (Thai ESG)"}
    ],
    asset: [
        { value: "ค่าซ่อมบ้านจากอุทกภัย", label: "ค่าซ่อมบ้านจากอุทกภัย" },
        { value: "ค่าซ่อมรถจากอุทกภัย", label: "ค่าซ่อมรถจากอุทกภัย" },
        { value: "เงินที่บริจาคแก่พรรคการเมือง", label: "เงินที่บริจาคแก่พรรคการเมือง" },
        { value: "ค่าท่องเที่ยวภายในประเทศ", label: "ค่าท่องเที่ยวภายในประเทศ" }
    ],
    easy: [
        { value: "Easy E-Receipt", label: "ค่าซื้อสินค้าหรือค่าบริการในระบบภาษีมูลค่าเพิ่ม" },
        { value: "Easy E-Receipt", label: "ค่าซื้อหนังสือ หนังสือพิมพ์ และนิตยสาร" },
        { value: "Easy E-Receipt", label: "ค่าซื้อหนังสือ e-book" },
        { value: "Easy E-Receipt", label: "ค่าซื้อสินค้า OTOP" }
    ],
    donation: [
        { value: "เงินบริจาคสนับสนุนการศึกษา/สถานพยาบาล/สภากาชาดไทย/อื่นๆ", label: "เงินบริจาคสนับสนุนการศึกษา/สถานพยาบาล/สภากาชาดไทย/อื่นๆ" },
        { value: "เงินบริจาค", label: "เงินบริจาค" },
    ]
};

const fieldConfig = {
    "อุปการะเลี้ยงดูบิดามารดา": ["doc_date"],
    "เบี้ยประกันสุขภาพบิดามารดา": ["doc_date", "total"],
    "อุปการะเลี้ยงดูคนพิการหรือคนทุพพลภาพ": ["doc_date"],
    "เบี้ยประกันชีวิต": ["doc_date", "warranty_period", "total"],
    "เบี้ยประกันสุขภาพ": ["doc_date", "total"],
    "เบี้ยประกันชีวิตแบบบำนาญ": ["doc_date", "warranty_period", "total"],
    "เงินสะสมกองทุนสำรองเลี้ยงชีพ": ["doc_date", "total", "net_income"],
    "เงินสะสมกองทุนบำเหน็จบำนาญ (กบข.)": ["doc_date", "total","net_income"],
    "เงินสะสมกองทุนสงเคราะห์ครูโรงเรียนเอกชน": ["doc_date", "total"],
    "เงินค่าชดเชยที่ได้รับตามกฎหมายแรงงาน (กรณีนำมารวมคำนวณภาษี)": ["doc_date", "total"],
    "เงินสะสมกองทุนการออมแห่งชาติ (กอช.)": ["doc_date", "total"],
    "ค่าซื้อหน่วยลงทุนในกองทุนรวมเพื่อการออม SSF": ["doc_date", "warranty_period", "ssf_total", "net_income"],
    "ค่าซื้อหน่วยลงทุนเพื่อการเลี้ยงชีพ (RMF)": ["doc_date", "warranty_period", "rmf_total", "net_income"],
    "เงินสมทบกองทุนประกันสังคม": ["total","career"],
    "ค่าซื้อหน่วยลงทุนในกองทุนรวมไทยเพื่อความยั่งยืน (Thai ESG)": ["doc_date", "total"],
    "ค่าซ่อมบ้านจากอุทกภัย": ["doc_date", "total"],
    "ค่าซ่อมรถจากอุทกภัย": ["doc_date", "total"],
    "เงินที่บริจาคแก่พรรคการเมือง": ["doc_date", "total"],
    "ค่าท่องเที่ยวภายในประเทศ": ["doc_date", "total", "invoice_no", "tax_id_seller", "forbidden_item_type","tax_id_buyer","seller"],
    "Easy E-Receipt": ["doc_date", "total", "invoice_no", "tax_id_seller", "forbidden_item_type","tax_id_buyer","seller"],
    "เงินบริจาคสนับสนุนการศึกษา/สถานพยาบาล/สภากาชาดไทย/อื่นๆ": ["doc_date", "total", "net_income"],
    "เงินบริจาค": ["doc_date", "total", "net_income"]
};

const careerOptions = [
  { value: "employee", label: "พนักงานประจำ" },
  { value: "freelance", label: "ฟรีแลนซ์ / รับจ้างอิสระ" },
  { value: "owner", label: "อาชีพอิสระ / ผู้ประกอบการ / อื่น ๆ" }
];

const fieldDefinitions = {
    doc_date: {
        label: "วันที่ในเอกสาร",
        type: "date",
        name: "doc_date"
    },
    warranty_period: {
        label: "ระยะเวลารับประกัน (ปี) / ถือหน่วยลงทุน (ปี)",
        type: "number",
        name: "warranty_period",
        attrs: { min: "0", step: "1", placeholder: "ระบุจำนวนปี" }
    },
    total: {
        label: "ยอดที่จ่ายตามเอกสาร (บาท)",
        type: "number",
        name: "total",
        attrs: { min: "0", step: "0.01", placeholder: "0.00" }
    },
    net_income: {
        label: "เงินได้หลังหักค่าใช้จ่ายแล้ว (บาท)",
        type: "number",
        name: "net_income",
        attrs: { min: "0", step: "0.01", placeholder: "0.00", title: "ใช้คำนวณเพดานสิทธิ์" }
    },
    ssf_total: {
        label: "ยอดซื้อ SSF (บาท)",
        type: "number",
        name: "ssf_total",
        attrs: { min: "0", step: "0.01", placeholder: "0.00" }
    },
    rmf_total: {
        label: "ยอดซื้อ RMF (บาท)",
        type: "number",
        name: "rmf_total",
        attrs: { min: "0", step: "0.01", placeholder: "0.00" }
    },
    invoice_no: {
        label: "เลขที่ใบกำกับภาษี",
        type: "text",
        name: "invoice_no",
        attrs: { placeholder: "ระบุเลขที่เอกสาร" }
    },
    seller: {
        label: "ชื่อร้านค้า",
        type: "text",
        name: "seller_manual",
        attrs: { placeholder: "ชื่อร้านค้า" }
    },
    tax_id_seller: {
        label: "เลขผู้เสียภาษีผู้ขาย (13 หลัก)",
        type: "text",
        name: "tax_id_seller",
        attrs: { maxlength: "13", placeholder: "ระบุเลข 13 หลัก" }

    },
    tax_id_buyer: {
        label: "เลขผู้เสียภาษีผู้ซื้อ (13 หลัก)",
        type: "text",
        name: "tax_id_buyer",
        attrs: { maxlength: "13", placeholder: "ระบุเลข 13 หลัก" }
        
    },
    issuer_brand: {
        label: "เเบรนผู้ขายคำ/โลโก้แบรนด์ที่อยู่",
        type: "text",
        name: "issuer_brand",
        attrs: { placeholder: "เช่น Big c ,CJ" }
    },

    forbidden_item_type: {
        label: "รายการสินค้า/บริการ (เลือกประเภทสินค้าต้องห้ามถ้ามี)",
        type: "select",
        name: "forbidden_item_type",
        options: [
            { value: "alcohol", label: "สุรา / เบียร์ / ไวน์" },
            { value: "tobacco", label: "ยาสูบ / บุหรี่" },
            { value: "fuel", label: "น้ำมัน / ก๊าซ / เชื้อเพลิง" },
            { value: "vehicle", label: "รถยนต์ / รถจักรยานยนต์ / เรือ" },
            { value: "utility", label: "ค่าน้ำ / ค่าไฟ / โทรศัพท์ / อินเทอร์เน็ต" },
            { value: "subscription", label: "บริการรายเดือน / รายปี / สมาชิก" },
            { value: "nonlife_insurance", label: "ประกันวินาศภัย / ประกันภัยรถยนต์" },
            { value: "other", label: "อื่น ๆ / ไม่อยู่ในรายการข้างต้น" }
        ]
    },
    career: {
        label: "อาชีพ",
        type: "select",
        name: "career",
        options: careerOptions
    }
};

// ==========================================
// ส่วนที่ 2: Logic สร้างฟอร์ม (DOM Logic)
// ==========================================
const mainSelect = document.getElementById("main-category");
const subSelect = document.getElementById("sub-category");
const dynamicFields = document.getElementById("dynamic-fields");

// Event: เมื่อเปลี่ยนหมวดหลัก
if (mainSelect) {
    mainSelect.addEventListener("change", () => {
        const key = mainSelect.value;
        populateSubCategory(key);
        renderFields(); // เคลียร์ฟิลด์เก่า
    });
}

// Event: เมื่อเปลี่ยนหมวดย่อย
if (subSelect) {
    subSelect.addEventListener("change", () => {
        renderFields();
    });
}

function populateSubCategory(mainKey) {
    subSelect.innerHTML = "";
    if (!mainKey || !subCategoriesByMain[mainKey]) {
        subSelect.disabled = true;
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "— เลือกหมวดหมู่หลักก่อน —";
        subSelect.appendChild(opt);
        return;
    }
    subSelect.disabled = false;
    const defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = "— โปรดเลือกหมวดหมู่ย่อย —";
    subSelect.appendChild(defaultOpt);
    subCategoriesByMain[mainKey].forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.value;
        opt.textContent = item.label;
        subSelect.appendChild(opt);
    });
}

function renderFields() {
    dynamicFields.innerHTML = "";
    const sub = subSelect.value;
    if (!sub) {
        // Show empty state
        const emptyState = document.createElement("div");
        emptyState.className = "empty-state";
        emptyState.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="48" height="48">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p>โปรดเลือกหมวดหมู่ย่อยก่อน ระบบจะแสดงช่องให้กรอกเฉพาะที่จำเป็น</p>
      `;
        dynamicFields.appendChild(emptyState);
        return;
    }
    const fields = fieldConfig[sub] || [];
    if (fields.length === 0) {
        const p = document.createElement("p");
        p.className = "hint-text";
        p.textContent = "หมวดหมู่นี้ยังไม่ได้กำหนดฟิลด์เฉพาะ สามารถเพิ่มภายหลังได้";
        dynamicFields.appendChild(p);
        return;
    }

    fields.forEach(code => {
        const def = fieldDefinitions[code];
        if (!def) return;

        const wrapper = document.createElement("div");
        wrapper.className = "form-group";

        const label = document.createElement("label");
        label.textContent = def.label;
        label.setAttribute("for", def.name);

        let fieldEl;

        if (def.type === "select") {
            const select = document.createElement("select");
            select.id = def.name;
            select.name = def.name;
            select.className = "form-control"; // เพิ่ม class ให้สวย

            const defaultOpt = document.createElement("option");
            defaultOpt.value = "";
            defaultOpt.textContent = "— โปรดเลือก —";
            select.appendChild(defaultOpt);

            (def.options || []).forEach(opt => {
                const o = document.createElement("option");
                o.value = opt.value;
                o.textContent = opt.label;
                select.appendChild(o);
            });
            fieldEl = select;
        } else {
            const input = document.createElement("input");
            input.type = def.type || "text";
            input.id = def.name;
            input.name = def.name;
            input.className = "form-control"; // เพิ่ม class ให้สวย

            if (def.attrs) {
                Object.entries(def.attrs).forEach(([k, v]) => input.setAttribute(k, v));
            }
            fieldEl = input;
        }

        wrapper.appendChild(label);
        wrapper.appendChild(fieldEl);
        dynamicFields.appendChild(wrapper);
    });
}

// ปุ่ม Reset
const resetBtn = document.querySelector('button[type="reset"]');
if (resetBtn) {
    resetBtn.addEventListener('click', () => {
        setTimeout(() => {
            subSelect.innerHTML = '<option value="">— เลือกหมวดหมู่หลักก่อน —</option>';
            subSelect.disabled = true;
            renderFields();
        }, 10);
    });
}

// ==========================================
// ส่วนที่ 3: Logic ส่งค่า (SEND DATA) 
// ==========================================
// document.addEventListener('DOMContentLoaded', () => {
//     // อ้างอิงปุ่มบันทึกและฟอร์ม
//     const saveBtn = document.getElementById("btn-save");
//     const form = document.getElementById("tax-form");
//     const summaryBox = document.getElementById("summary-box");

//     // ถ้าไม่มีปุ่มนี้ในหน้านั้น ให้จบการทำงาน
//     if (!saveBtn) return;

//     saveBtn.addEventListener("click", async (e) => {
//         e.preventDefault(); // ห้าม Refresh

//         // 1. ดึงหมวดหมู่ (ดึงแยกจาก form เพราะบางที select disabled แล้วค่าไม่ส่ง)
//         const mainCatValue = mainSelect.value;
//         const subCatValue = subSelect.value;
//         const subCatLabel = subSelect.options[subSelect.selectedIndex]?.text || "";

//         if (!subCatValue) {
//             alert("กรุณาเลือกหมวดหมู่ให้ครบถ้วน");
//             return;
//         }

//         // 2. ดึงข้อมูลจาก Form
//         const fd = new FormData(form);

//         // 3. แปลงวันที่ (YYYY-MM-DD -> Object)
//         const rawDate = fd.get("doc_date");
//         let dateObj = {};
//         if (rawDate) {
//             const parts = rawDate.split("-");
//             if (parts.length === 3) {
//                 dateObj = {
//                     year: parseInt(parts[0]),
//                     month: parseInt(parts[1]),
//                     day: parseInt(parts[2])
//                 };
//             }
//         }

//         // 4. แปลง Items (Dropdown -> Array)
//         const itemType = fd.get("forbidden_item_type");
//         let itemsArray = [];
//         itemsArray.push({
//             // ถ้าเลือกของต้องห้าม ให้ส่งชื่อนั้น ถ้าไม่เลือก ให้ส่งชื่อหมวด
//             name: (itemType && itemType !== "none") ? itemType : subCatLabel,
//             total_price: parseFloat(fd.get("total") || 0)
//         });

//         // 5. รวมร่างข้อมูล (Payload)
//         const payload = {
//             buyer: fd.get("user_name") || "",
//             main_category: mainCatValue,
//             sub_category: subCatLabel, // Python ใช้ตัวนี้เช็ค
            
//             date: dateObj,
//             total: parseFloat(fd.get("total") || 0),
//             net_income: parseFloat(fd.get("net_income") || 0),
//             warranty_period: parseInt(fd.get("warranty_period") || 0),
            
//             ssf_total: parseFloat(fd.get("ssf_total") || 0),
//             rmf_total: parseFloat(fd.get("rmf_total") || 0),
            
//             invoice_no: fd.get("invoice_no") || "",
//             tax_id_seller: fd.get("tax_id_seller") || "",
//             career: fd.get("career") || "employee",
//             tax_id_buyer: fd.get("tax_id_buyer") || "",
//             issuer_brand: fd.get("issuer_brand") || "",
//             seller: fd.get("seller_manual") || "",
            
//             items: itemsArray, 
//         };

//         console.log("Sending:", payload);

//         // 6. ส่งไป Python
//         try {
//             // const res = await fetch("/api/check", {
//             const res = await fetch(`${API_BASE}/api/check`, {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify(payload)
//             });

//             const data = await res.json();

//             if (data.ok) {
//                 const r = data.result;

//                 // 1. เช็คสถานะว่าเป็น "ไม่สามารถลดหย่อนได้" หรือไม่
//                 const isError = r.deduction_status === "ไม่สามารถลดหย่อนได้";

//                 // 2. กำหนดสีตามสถานะ (Ternary Operator)
//                 // ถ้าไม่ผ่าน (isError) ให้ใช้สีแดง, ถ้าผ่าน ให้ใช้สีเขียวเดิม
//                 const styles = {
//                     bg: isError ? "#fef2f2" : "#f0fdf4",        // พื้นหลัง (แดงอ่อน / เขียวอ่อน)
//                     border: isError ? "#fecaca" : "#bbf7d0",    // ขอบ (แดง / เขียว)
//                     text: isError ? "#dc2626" : "#166534"       // ตัวหนังสือหัวข้อ (แดงเข้ม / เขียวเข้ม)
//                 };

//                 // 3. แสดงผลลัพธ์โดยใช้สีที่กำหนดไว้ข้างบน
//                 summaryBox.innerHTML = `
//                     <div style="padding: 15px; border-radius: 8px; background: ${styles.bg}; border: 1px solid ${styles.border};">
//                         <h3 style="color: ${styles.text}; margin-bottom: 10px;">
//                             ${r.deduction_status}
//                         </h3>
//                         <p><strong>ยอดลดหย่อน:</strong> ${r.final_deduction || "0"} บาท</p>
//                         <hr style="margin: 10px 0; border-color: ${styles.border};">
//                         <p style="font-size: 0.9em; color: #555;">
//                             <strong>รายละเอียด/เหตุผล:</strong> ${r.reason || r.final_deduction_rule || "-"}
//                         </p>
//                     </div>
//                 `;
//             } else {
//                 alert("เกิดข้อผิดพลาด: " + (data.error || "Unknown Error"));
//             }

//         } catch (err) {
//             console.error(err);
//             alert("เชื่อมต่อ Server ไม่ได้! (เช็คว่าเปิด app.py หรือยัง)");
//         }
//     });
// });
document.addEventListener('DOMContentLoaded', () => {
    const saveBtn = document.getElementById("btn-save");
    const form = document.getElementById("tax-form");
    const summaryBox = document.getElementById("summary-box");

    if (!saveBtn || !form || !summaryBox) {
        console.warn("ไม่เจอ element ที่ต้องใช้ (btn-save / tax-form / summary-box)");
        return;
    }

    saveBtn.addEventListener("click", async (e) => {
        e.preventDefault(); // ห้าม refresh หน้า

        const mainCatValue = mainSelect.value;
        const subCatValue = subSelect.value;
        const subCatLabel = subSelect.options[subSelect.selectedIndex]?.text || "";

        if (!subCatValue) {
            alert("กรุณาเลือกหมวดหมู่ให้ครบถ้วน");
            return;
        }

        const fd = new FormData(form);

        // แปลงวันที่
        const rawDate = fd.get("doc_date");
        let dateObj = {};
        if (rawDate) {
            const parts = rawDate.split("-");
            if (parts.length === 3) {
                dateObj = {
                    year: parseInt(parts[0]),
                    month: parseInt(parts[1]),
                    day: parseInt(parts[2])
                };
            }
        }

        // items
        const itemType = fd.get("forbidden_item_type");
        const itemsArray = [{
            name: (itemType && itemType !== "none") ? itemType : subCatLabel,
            total_price: parseFloat(fd.get("total") || 0)
        }];

        const payload = {
            buyer: fd.get("user_name") || "",
            main_category: mainCatValue,
            sub_category: subCatLabel,

            date: dateObj,
            total: parseFloat(fd.get("total") || 0),
            net_income: parseFloat(fd.get("net_income") || 0),
            warranty_period: parseInt(fd.get("warranty_period") || 0),

            ssf_total: parseFloat(fd.get("ssf_total") || 0),
            rmf_total: parseFloat(fd.get("rmf_total") || 0),

            invoice_no: fd.get("invoice_no") || "",
            tax_id_seller: fd.get("tax_id_seller") || "",
            career: fd.get("career") || "employee",
            tax_id_buyer: fd.get("tax_id_buyer") || "",
            issuer_brand: fd.get("issuer_brand") || "",
            seller: fd.get("seller_manual") || "",

            items: itemsArray,
        };

        console.log(">>> ส่ง payload ไป check:", payload);

        try {
            const res = await fetch(`${API_BASE}/api/check`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            console.log(">>> res status:", res.status, res.statusText);

            if (!res.ok) {
                alert("เซิร์ฟเวอร์ตอบกลับผิดปกติ (HTTP " + res.status + ")");
                return;
            }

            let data;
            try {
                data = await res.json();
            } catch (err) {
                console.error("parse JSON fail:", err);
                alert("รูปแบบข้อมูลตอบกลับไม่ถูกต้อง (parse JSON ไม่ได้)");
                return;
            }

            console.log(">>> data จาก backend:", data);

            if (data.ok) {
                const r = data.result || {};

                const isError = r.deduction_status === "ไม่สามารถลดหย่อนได้";
                const styles = {
                    bg: isError ? "#fef2f2" : "#f0fdf4",
                    border: isError ? "#fecaca" : "#bbf7d0",
                    text: isError ? "#dc2626" : "#166534"
                };

                summaryBox.innerHTML = `
                    <div style="padding: 15px; border-radius: 8px; background: ${styles.bg}; border: 1px solid ${styles.border};">
                        <h3 style="color: ${styles.text}; margin-bottom: 10px;">
                            ${r.deduction_status || "—"}
                        </h3>
                        <p><strong>ยอดลดหย่อน:</strong> ${r.final_deduction ?? "0"} บาท</p>
                        <hr style="margin: 10px 0; border-color: ${styles.border};">
                        <p style="font-size: 0.9em; color: #555;">
                            <strong>รายละเอียด/เหตุผล:</strong> ${r.reason || r.final_deduction_rule || "-"}
                        </p>
                    </div>
                `;
            } else {
                alert("เกิดข้อผิดพลาด: " + (data.error || "Unknown Error"));
            }

        } catch (err) {
            console.error("fetch error:", err);
            alert("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ (backend ล่มหรือเน็ตมีปัญหา)");
        }
    });
});