# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Excel Data Processor</title>
#     <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
#     <style>
#         * {
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }

#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             min-height: 100vh;
#             padding: 20px;
#         }

#         .container {
#             max-width: 1200px;
#             margin: 0 auto;
#             background: white;
#             border-radius: 20px;
#             box-shadow: 0 20px 40px rgba(0,0,0,0.1);
#             overflow: hidden;
#         }

#         .header {
#             background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
#             color: white;
#             padding: 30px;
#             text-align: center;
#         }

#         .header h1 {
#             font-size: 2.5rem;
#             margin-bottom: 10px;
#             font-weight: 300;
#         }

#         .header p {
#             font-size: 1.1rem;
#             opacity: 0.9;
#         }

#         .main-content {
#             padding: 40px;
#         }

#         .section {
#             margin-bottom: 40px;
#             padding: 30px;
#             border-radius: 15px;
#             background: #f8f9fa;
#             border: 1px solid #e9ecef;
#             transition: all 0.3s ease;
#         }

#         .section:hover {
#             box-shadow: 0 5px 15px rgba(0,0,0,0.1);
#         }

#         .section h2 {
#             color: #2c3e50;
#             margin-bottom: 20px;
#             font-size: 1.5rem;
#             display: flex;
#             align-items: center;
#             gap: 10px;
#         }

#         .icon {
#             width: 24px;
#             height: 24px;
#             background: #667eea;
#             border-radius: 50%;
#             display: inline-flex;
#             align-items: center;
#             justify-content: center;
#             color: white;
#             font-weight: bold;
#         }

#         .form-group {
#             margin-bottom: 20px;
#         }

#         .form-row {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
#             gap: 20px;
#         }

#         label {
#             display: block;
#             margin-bottom: 8px;
#             font-weight: 600;
#             color: #2c3e50;
#         }

#         input, select, textarea {
#             width: 100%;
#             padding: 12px 15px;
#             border: 2px solid #e9ecef;
#             border-radius: 8px;
#             font-size: 14px;
#             transition: all 0.3s ease;
#         }

#         input:focus, select:focus, textarea:focus {
#             outline: none;
#             border-color: #667eea;
#             box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
#         }

#         .upload-area {
#             border: 3px dashed #667eea;
#             border-radius: 15px;
#             padding: 40px 20px;
#             text-align: center;
#             background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
#             cursor: pointer;
#             transition: all 0.3s ease;
#         }

#         .upload-area:hover {
#             border-color: #5a67d8;
#             background: linear-gradient(135deg, #f0f2ff 0%, #e8ebff 100%);
#         }

#         .upload-area.dragover {
#             border-color: #4c51bf;
#             background: linear-gradient(135deg, #e8ebff 0%, #ddd6fe 100%);
#         }

#         .upload-icon {
#             font-size: 48px;
#             color: #667eea;
#             margin-bottom: 15px;
#         }

#         .file-input {
#             display: none;
#         }

#         .file-list {
#             margin-top: 20px;
#         }

#         .file-item {
#             display: flex;
#             align-items: center;
#             justify-content: space-between;
#             padding: 12px 15px;
#             background: white;
#             border: 1px solid #e9ecef;
#             border-radius: 8px;
#             margin-bottom: 10px;
#         }

#         .file-info {
#             display: flex;
#             align-items: center;
#             gap: 10px;
#         }

#         .file-size {
#             font-size: 12px;
#             color: #6c757d;
#             background: #f8f9fa;
#             padding: 4px 8px;
#             border-radius: 4px;
#         }

#         .remove-file {
#             background: #dc3545;
#             color: white;
#             border: none;
#             padding: 5px 10px;
#             border-radius: 4px;
#             cursor: pointer;
#             font-size: 12px;
#         }

#         .remove-file:hover {
#             background: #c82333;
#         }

#         .btn {
#             padding: 15px 30px;
#             border: none;
#             border-radius: 8px;
#             font-size: 16px;
#             font-weight: 600;
#             cursor: pointer;
#             transition: all 0.3s ease;
#             text-decoration: none;
#             display: inline-flex;
#             align-items: center;
#             gap: 10px;
#         }

#         .btn-primary {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#         }

#         .btn-primary:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
#         }

#         .btn-success {
#             background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
#             color: white;
#         }

#         .btn-success:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 10px 20px rgba(40, 167, 69, 0.3);
#         }

#         .btn:disabled {
#             opacity: 0.6;
#             cursor: not-allowed;
#             transform: none !important;
#         }

#         .progress {
#             width: 100%;
#             height: 20px;
#             background: #e9ecef;
#             border-radius: 10px;
#             overflow: hidden;
#             margin: 20px 0;
#         }

#         .progress-bar {
#             height: 100%;
#             background: linear-gradient(90deg, #667eea, #764ba2);
#             transition: width 0.3s ease;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             color: white;
#             font-size: 12px;
#             font-weight: 600;
#         }

#         .status {
#             padding: 15px;
#             border-radius: 8px;
#             margin: 20px 0;
#             font-weight: 600;
#         }

#         .status.success {
#             background: #d1edff;
#             color: #0c5460;
#             border: 1px solid #b8daff;
#         }

#         .status.error {
#             background: #f8d7da;
#             color: #721c24;
#             border: 1px solid #f5c6cb;
#         }

#         .status.info {
#             background: #d1ecf1;
#             color: #0c5460;
#             border: 1px solid #bee5eb;
#         }

#         .results {
#             margin-top: 30px;
#         }

#         .download-item {
#             display: flex;
#             align-items: center;
#             justify-content: space-between;
#             padding: 15px;
#             background: #f8f9fa;
#             border: 1px solid #e9ecef;
#             border-radius: 8px;
#             margin-bottom: 10px;
#         }

#         @media (max-width: 768px) {
#             .main-content {
#                 padding: 20px;
#             }
            
#             .form-row {
#                 grid-template-columns: 1fr;
#             }
            
#             .header h1 {
#                 font-size: 2rem;
#             }
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <h1>📊 Excel Data Processor</h1>
#             <p>Upload your files, configure parameters, and download processed results</p>
#         </div>

#         <div class="main-content">
#             <!-- Configuration Section -->
#             <div class="section">
#                 <h2><span class="icon">⚙</span>Configuration Parameters</h2>
#                 <div class="form-row">
#                     <div class="form-group">
#                         <label for="startDate">Start Date:</label>
#                         <input type="date" id="startDate" value="2020-03-01">
#                     </div>
#                     <div class="form-group">
#                         <label for="endDate">End Date:</label>
#                         <input type="date" id="endDate" value="2020-03-31">
#                     </div>
#                 </div>
                
#                 <div class="form-row">
#                     <div class="form-group">
#                         <label for="totalAmount">Total Amount:</label>
#                         <input type="number" id="totalAmount" value="8000000" min="0" step="0.01">
#                     </div>
#                     <div class="form-group">
#                         <label for="gstRate">GST Rate (%):</label>
#                         <input type="number" id="gstRate" value="0" min="0" max="100" step="0.01">
#                     </div>
#                 </div>

#                 <div class="form-group">
#                     <label for="state">State:</label>
#                     <input type="text" id="state" value="Telangana">
#                 </div>

#                 <div class="form-group">
#                     <label for="districts">Districts (comma-separated):</label>
#                     <textarea id="districts" rows="3">Adilabad, Khammam, Warangal, Hyderabad, Karim Nagar, Nalgonda</textarea>
#                 </div>

#                 <div class="form-row">
#                     <div class="form-group">
#                         <label for="marketLinkagesPercent">Market Linkages Trading (%):</label>
#                         <input type="number" id="marketLinkagesPercent" value="30" min="0" max="100" step="0.1">
#                     </div>
#                     <div class="form-group">
#                         <label for="agriPercent">Agri Inputs (%):</label>
#                         <input type="number" id="agriPercent" value="25" min="0" max="100" step="0.1">
#                     </div>
#                     <div class="form-group">
#                         <label for="fmcgPercent">FMCG (%):</label>
#                         <input type="number" id="fmcgPercent" value="45" min="0" max="100" step="0.1">
#                     </div>
#                 </div>
#             </div>

#             <!-- File Upload Section -->
#             <div class="section">
#                 <h2><span class="icon">📁</span>File Upload</h2>
#                 <div class="upload-area" onclick="document.getElementById('fileInput').click()">
#                     <div class="upload-icon">📤</div>
#                     <h3>Click here or drag & drop your Excel files</h3>
#                     <p>Supports .xlsx, .xls files up to 100MB each</p>
#                     <input type="file" id="fileInput" class="file-input" multiple accept=".xlsx,.xls" onchange="handleFiles(event.target.files)">
#                 </div>
                
#                 <div id="fileList" class="file-list"></div>
#             </div>

#             <!-- Process Section -->
#             <div class="section">
#                 <h2><span class="icon">🔄</span>Processing</h2>
#                 <button id="processBtn" class="btn btn-primary" onclick="processFiles()">
#                     🚀 Process Files
#                 </button>
                
#                 <div id="progress" class="progress" style="display: none;">
#                     <div id="progressBar" class="progress-bar" style="width: 0%;">0%</div>
#                 </div>
                
#                 <div id="status"></div>
                
#                 <div id="results" class="results" style="display: none;">
#                     <h3>📥 Download Results:</h3>
#                     <div id="downloadLinks"></div>
#                 </div>
#             </div>
#         </div>
#     </div>

#     <script>
#         let uploadedFiles = [];

#         // Drag and drop functionality
#         const uploadArea = document.querySelector('.upload-area');
        
#         uploadArea.addEventListener('dragover', (e) => {
#             e.preventDefault();
#             uploadArea.classList.add('dragover');
#         });
        
#         uploadArea.addEventListener('dragleave', () => {
#             uploadArea.classList.remove('dragover');
#         });
        
#         uploadArea.addEventListener('drop', (e) => {
#             e.preventDefault();
#             uploadArea.classList.remove('dragover');
#             handleFiles(e.dataTransfer.files);
#         });

#         function handleFiles(files) {
#             const fileList = document.getElementById('fileList');
            
#             for (let file of files) {
#                 if (file.type.includes('sheet') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
#                     if (file.size > 100 * 1024 * 1024) {
#                         showStatus('File ' + file.name + ' is too large (>100MB)', 'error');
#                         continue;
#                     }
                    
#                     uploadedFiles.push(file);
                    
#                     const fileItem = document.createElement('div');
#                     fileItem.className = 'file-item';
#                     fileItem.innerHTML = `
#                         <div class="file-info">
#                             <span>📄</span>
#                             <span>${file.name}</span>
#                             <span class="file-size">${formatFileSize(file.size)}</span>
#                         </div>
#                         <button class="remove-file" onclick="removeFile('${file.name}')">Remove</button>
#                     `;
                    
#                     fileList.appendChild(fileItem);
#                 } else {
#                     showStatus('Invalid file type: ' + file.name, 'error');
#                 }
#             }
#         }

#         function removeFile(fileName) {
#             uploadedFiles = uploadedFiles.filter(file => file.name !== fileName);
#             updateFileList();
#         }

#         function updateFileList() {
#             const fileList = document.getElementById('fileList');
#             fileList.innerHTML = '';
#             uploadedFiles.forEach(file => {
#                 const fileItem = document.createElement('div');
#                 fileItem.className = 'file-item';
#                 fileItem.innerHTML = `
#                     <div class="file-info">
#                         <span>📄</span>
#                         <span>${file.name}</span>
#                         <span class="file-size">${formatFileSize(file.size)}</span>
#                     </div>
#                     <button class="remove-file" onclick="removeFile('${file.name}')">Remove</button>
#                 `;
#                 fileList.appendChild(fileItem);
#             });
#         }

#         function formatFileSize(bytes) {
#             if (bytes === 0) return '0 Bytes';
#             const k = 1024;
#             const sizes = ['Bytes', 'KB', 'MB', 'GB'];
#             const i = Math.floor(Math.log(bytes) / Math.log(k));
#             return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
#         }

#         function showStatus(message, type = 'info') {
#             const status = document.getElementById('status');
#             status.className = `status ${type}`;
#             status.textContent = message;
#             status.style.display = 'block';
#         }

#         function validatePercentages() {
#             const market = parseFloat(document.getElementById('marketLinkagesPercent').value);
#             const agri = parseFloat(document.getElementById('agriPercent').value);
#             const fmcg = parseFloat(document.getElementById('fmcgPercent').value);
            
#             const total = market + agri + fmcg;
#             if (Math.abs(total - 100) > 0.01) {
#                 showStatus(`Percentages must add up to 100%. Current total: ${total.toFixed(1)}%`, 'error');
#                 return false;
#             }
#             return true;
#         }

#         async function processFiles() {
#             if (uploadedFiles.length === 0) {
#                 showStatus('Please upload at least one file', 'error');
#                 return;
#             }
            
#             if (!validatePercentages()) {
#                 return;
#             }

#             const processBtn = document.getElementById('processBtn');
#             const progress = document.getElementById('progress');
#             const progressBar = document.getElementById('progressBar');
#             const results = document.getElementById('results');
            
#             processBtn.disabled = true;
#             progress.style.display = 'block';
#             results.style.display = 'none';
            
#             try {
#                 showStatus('Processing files...', 'info');
                
#                 // Get configuration
#                 const config = {
#                     startDate: document.getElementById('startDate').value,
#                     endDate: document.getElementById('endDate').value,
#                     totalAmount: parseFloat(document.getElementById('totalAmount').value),
#                     gstRate: parseFloat(document.getElementById('gstRate').value) / 100,
#                     state: document.getElementById('state').value,
#                     districts: document.getElementById('districts').value.split(',').map(d => d.trim()),
#                     marketLinkagesPercent: parseFloat(document.getElementById('marketLinkagesPercent').value) / 100,
#                     agriPercent: parseFloat(document.getElementById('agriPercent').value) / 100,
#                     fmcgPercent: parseFloat(document.getElementById('fmcgPercent').value) / 100
#                 };
                
#                 const downloadLinks = document.getElementById('downloadLinks');
#                 downloadLinks.innerHTML = '';
                
#                 for (let i = 0; i < uploadedFiles.length; i++) {
#                     const file = uploadedFiles[i];
#                     const progress_percent = ((i + 1) / uploadedFiles.length) * 100;
                    
#                     progressBar.style.width = progress_percent + '%';
#                     progressBar.textContent = `Processing ${file.name}... ${Math.round(progress_percent)}%`;
                    
#                     // Process the file (simplified simulation)
#                     await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate processing time
                    
#                     const processedData = await processExcelFile(file, config);
#                     const downloadItem = createDownloadLink(file.name, processedData);
#                     downloadLinks.appendChild(downloadItem);
#                 }
                
#                 progressBar.style.width = '100%';
#                 progressBar.textContent = 'Complete!';
#                 showStatus('All files processed successfully!', 'success');
#                 results.style.display = 'block';
                
#             } catch (error) {
#                 showStatus('Error processing files: ' + error.message, 'error');
#             } finally {
#                 processBtn.disabled = false;
#                 setTimeout(() => {
#                     progress.style.display = 'none';
#                 }, 2000);
#             }
#         }

#         async function processExcelFile(file, config) {
#             return new Promise((resolve, reject) => {
#                 const reader = new FileReader();
#                 reader.onload = function(e) {
#                     try {
#                         const data = new Uint8Array(e.target.result);
#                         const workbook = XLSX.read(data, { type: 'array' });
                        
#                         // Generate processed data based on your logic
#                         const processedData = generateProcessedData(config);
                        
#                         // Create new workbook with processed data
#                         const ws = XLSX.utils.json_to_sheet(processedData);
#                         const wb = XLSX.utils.book_new();
#                         XLSX.utils.book_append_sheet(wb, ws, "Processed Data");
                        
#                         resolve(wb);
#                     } catch (error) {
#                         reject(error);
#                     }
#                 };
#                 reader.onerror = () => reject(new Error('Failed to read file'));
#                 reader.readAsArrayBuffer(file);
#             });
#         }

#         function generateProcessedData(config) {
#             const data = [];
#             const startDate = new Date(config.startDate);
#             const endDate = new Date(config.endDate);
            
#             // Calculate amounts
#             const marketLinkagesTotal = Math.round(config.totalAmount * config.marketLinkagesPercent * 100) / 100;
#             const agriTotal = Math.round(config.totalAmount * config.agriPercent * 100) / 100;
#             const fmcgTotal = Math.round(config.totalAmount * config.fmcgPercent * 100) / 100;
            
#             // Generate dates (90% random selection as in original code)
#             const allDates = [];
#             const currentDate = new Date(startDate);
#             while (currentDate <= endDate) {
#                 allDates.push(new Date(currentDate));
#                 currentDate.setDate(currentDate.getDate() + 1);
#             }
            
#             // Select 90% of dates randomly
#             const selectedDates = [];
#             const numDates = Math.floor(allDates.length * 0.9);
#             const shuffledDates = [...allDates].sort(() => 0.5 - Math.random());
#             for (let i = 0; i < numDates; i++) {
#                 selectedDates.push(shuffledDates[i]);
#             }
#             selectedDates.sort((a, b) => a - b);
            
#             // Generate data for each date and district
#             selectedDates.forEach(date => {
#                 config.districts.forEach(district => {
#                     // FMCG
#                     data.push({
#                         Date: date.toISOString().split('T')[0],
#                         'Sub Vertical': 'FMCG',
#                         Vertical: 'Commerce Business',
#                         State: config.state,
#                         District: district,
#                         'GST Rate': config.gstRate,
#                         'Taxable_Amount': Math.random() * 8000 + 1000 // Random amount, will be normalized
#                     });
                    
#                     // Agri Inputs
#                     data.push({
#                         Date: date.toISOString().split('T')[0],
#                         'Sub Vertical': 'Agri Inputs',
#                         Vertical: 'Agri Business',
#                         State: config.state,
#                         District: district,
#                         'GST Rate': config.gstRate,
#                         'Taxable_Amount': Math.random() * 3500 + 500
#                     });
                    
#                     // Market Linkages Trading
#                     data.push({
#                         Date: date.toISOString().split('T')[0],
#                         'Sub Vertical': 'Market Linkages Trading',
#                         Vertical: 'Agri Business',
#                         State: config.state,
#                         District: district,
#                         'GST Rate': config.gstRate,
#                         'Taxable_Amount': Math.random() * 4000 + 1000
#                     });
#                 });
#             });
            
#             // Normalize amounts to match target totals
#             normalizeAmounts(data, 'FMCG', fmcgTotal);
#             normalizeAmounts(data, 'Agri Inputs', agriTotal);
#             normalizeAmounts(data, 'Market Linkages Trading', marketLinkagesTotal);
            
#             // Add percentage column
#             data.forEach(row => {
#                 row['percentage_of_total'] = (row['Taxable_Amount'] / config.totalAmount) * 100;
#             });
            
#             return data;
#         }

#         function normalizeAmounts(data, subVertical, targetTotal) {
#             const items = data.filter(row => row['Sub Vertical'] === subVertical);
#             const currentTotal = items.reduce((sum, item) => sum + item['Taxable_Amount'], 0);
#             const ratio = targetTotal / currentTotal;
            
#             items.forEach(item => {
#                 item['Taxable_Amount'] = Math.round(item['Taxable_Amount'] * ratio * 100) / 100;
#             });
#         }

#         function createDownloadLink(originalFileName, workbook) {
#             const downloadItem = document.createElement('div');
#             downloadItem.className = 'download-item';
            
#             const processedFileName = originalFileName.replace(/\.[^/.]+$/, "_processed.xlsx");
            
#             downloadItem.innerHTML = `
#                 <div class="file-info">
#                     <span>📊</span>
#                     <span>${processedFileName}</span>
#                 </div>
#                 <button class="btn btn-success" onclick="downloadFile('${processedFileName}', arguments[0])">
#                     📥 Download
#                 </button>
#             `;
            
#             // Store workbook data in element for download
#             downloadItem.dataset.workbook = JSON.stringify(workbook);
            
#             return downloadItem;
#         }

#         function downloadFile(fileName, element) {
#             const workbook = JSON.parse(element.closest('.download-item').dataset.workbook);
#             const wbout = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
            
#             const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
#             const url = URL.createObjectURL(blob);
            
#             const link = document.createElement('a');
#             link.href = url;
#             link.download = fileName;
#             document.body.appendChild(link);
#             link.click();
#             document.body.removeChild(link);
#             URL.revokeObjectURL(url);
#         }

#         // Auto-update percentage validation
#         document.getElementById('marketLinkagesPercent').addEventListener('input', updatePercentageDisplay);
#         document.getElementById('agriPercent').addEventListener('input', updatePercentageDisplay);
#         document.getElementById('fmcgPercent').addEventListener('input', updatePercentageDisplay);

#         function updatePercentageDisplay() {
#             const market = parseFloat(document.getElementById('marketLinkagesPercent').value) || 0;
#             const agri = parseFloat(document.getElementById('agriPercent').value) || 0;
#             const fmcg = parseFloat(document.getElementById('fmcgPercent').value) || 0;
#             const total = market + agri + fmcg;
            
#             // Update input styles based on total
#             const inputs = [
#                 document.getElementById('marketLinkagesPercent'),
#                 document.getElementById('agriPercent'),
#                 document.getElementById('fmcgPercent')
#             ];
            
#             inputs.forEach(input => {
#                 if (Math.abs(total - 100) > 0.01) {
#                     input.style.borderColor = '#dc3545';
#                 } else {
#                     input.style.borderColor = '#28a745';
#                 }
#             });
#         }
#     </script>
# </body>
# </html>