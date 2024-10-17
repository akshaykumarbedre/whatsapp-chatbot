document.addEventListener('DOMContentLoaded', function() {
    const businessInfoForm = document.getElementById('business-info-form');
    const productForm = document.getElementById('product-form');
    const faqForm = document.getElementById('faq-form');
    const productList = document.getElementById('product-list');
    const faqList = document.getElementById('faq-list');

    // Fetch and display existing data
    fetchExistingData();

    
    function fetchExistingData() {
        // Fetch existing products
        fetch('/get_products')
            .then(response => response.json())
            .then(products => {
                productList.innerHTML = '';
                products.forEach(product => {
                    addProductToList(product);
                });
            });

        // Fetch existing FAQs
        fetch('/get_faqs')
            .then(response => response.json())
            .then(faqs => {
                faqList.innerHTML = '';
                faqs.forEach(faq => {
                    addFAQToList(faq);
                });
            });
            
        fetch('/get_business_info')
            .then(response => response.json())
            .then(businessInfo => {
                document.getElementById('business-name').value = businessInfo.name || '';
                document.getElementById('business-description').value = businessInfo.description || '';
                document.getElementById('brand-voice').value = businessInfo.brandVoice || '';
            });
    }

    businessInfoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const businessInfo = {
            name: document.getElementById('business-name').value,
            description: document.getElementById('business-description').value,
            brandVoice: document.getElementById('brand-voice').value
        };
        fetch('/save_business_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(businessInfo),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Business information saved successfully!');
            }
        });
    });

    productForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const product = {
            name: document.getElementById('product-name').value,
            price: parseFloat(document.getElementById('product-price').value),
            type: document.getElementById('product-type').value,
            quantity: parseInt(document.getElementById('product-quantity').value),
            description: document.getElementById('product-description').value
        };
        fetch('/add_product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(product),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Product added successfully!');
                product.id = data.id;
                addProductToList(product);
                productForm.reset();
            }
        });
    });

    faqForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const faq = {
            question: document.getElementById('faq-question').value,
            answer: document.getElementById('faq-answer').value
        };
        fetch('/add_faq', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(faq),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('FAQ added successfully!');
                faq.id = data.id;
                addFAQToList(faq);
                faqForm.reset();
            }
        });
    });

    // CSV upload functionality for products
    document.getElementById('upload-product-csv').addEventListener('click', function() {
        const file = document.getElementById('product-csv-file').files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const csv = e.target.result;
                const lines = csv.split('\n');
                const headers = lines[0].split(',');
                for (let i = 1; i < lines.length; i++) {
                    const values = lines[i].split(',');
                    if (values.length === headers.length) {
                        const product = {};
                        headers.forEach((header, index) => {
                            product[header.trim()] = values[index].trim();
                        });
                        addProductToList(product);
                    }
                }
            };
            reader.readAsText(file);
        }
    });

    // CSV upload functionality for FAQs
    document.getElementById('upload-faq-csv').addEventListener('click', function() {
        const file = document.getElementById('faq-csv-file').files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const csv = e.target.result;
                const lines = csv.split('\n');
                for (let i = 1; i < lines.length; i++) {
                    const [question, answer] = lines[i].split(',');
                    if (question && answer) {
                        addFAQToList({ question: question.trim(), answer: answer.trim() });
                    }
                }
            };
            reader.readAsText(file);
        }
    });

    function addProductToList(product) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span>${product.name}</span><input type="text" value="${product.name}"></td>
            <td><span>$${product.price}</span><input type="number" value="${product.price}"></td>
            <td><span>${product.type}</span><input type="text" value="${product.type}"></td>
            <td><span>${product.quantity}</span><input type="number" value="${product.quantity}"></td>
            <td><span>${product.description}</span><textarea>${product.description}</textarea></td>
            <td>
                <button class="edit-btn">Edit</button>
                <button class="save-btn" style="display:none;">Save</button>
                <button class="delete-btn">Delete</button>
            </td>
        `;
        row.dataset.id = product.id;
        row.classList.add('view-mode');
        productList.appendChild(row);

        const editBtn = row.querySelector('.edit-btn');
        const saveBtn = row.querySelector('.save-btn');
        const deleteBtn = row.querySelector('.delete-btn');

        editBtn.addEventListener('click', () => {
            row.classList.remove('view-mode');
            row.classList.add('edit-mode');
            editBtn.style.display = 'none';
            saveBtn.style.display = 'inline-block';
        });

        saveBtn.addEventListener('click', () => {
            const updatedProduct = {
                id: product.id,
                name: row.querySelector('input[type="text"]').value,
                price: parseFloat(row.querySelectorAll('input[type="number"]')[0].value),
                type: row.querySelectorAll('input[type="text"]')[1].value,
                quantity: parseInt(row.querySelectorAll('input[type="number"]')[1].value),
                description: row.querySelector('textarea').value
            };
            updateProduct(updatedProduct, row);
        });

        deleteBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete this product?')) {
                deleteProduct(product.id, row);
            }
        });
    }

    function addFAQToList(faq) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span>${faq.question}</span><input type="text" value="${faq.question}"></td>
            <td><span>${faq.answer}</span><textarea>${faq.answer}</textarea></td>
            <td>
                <button class="edit-btn">Edit</button>
                <button class="save-btn" style="display:none;">Save</button>
                <button class="delete-btn">Delete</button>
            </td>
        `;
        row.classList.add('view-mode');
        faqList.appendChild(row);

        const editBtn = row.querySelector('.edit-btn');
        const saveBtn = row.querySelector('.save-btn');
        const deleteBtn = row.querySelector('.delete-btn');

        editBtn.addEventListener('click', () => {
            row.classList.remove('view-mode');
            row.classList.add('edit-mode');
            editBtn.style.display = 'none';
            saveBtn.style.display = 'inline-block';
        });

        saveBtn.addEventListener('click', () => {
            const updatedFAQ = {
                oldQuestion: faq.question,
                question: row.querySelector('input[type="text"]').value,
                answer: row.querySelector('textarea').value
            };
            updateFAQ(updatedFAQ, row);
        });

        deleteBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete this FAQ?')) {
                deleteFAQ(faq.question, row);
            }
        });
    }



    function updateProduct(product, row) {
        fetch('/update_product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(product),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Product updated successfully!');
                row.classList.remove('edit-mode');
                row.classList.add('view-mode');
                row.querySelector('.edit-btn').style.display = 'inline-block';
                row.querySelector('.save-btn').style.display = 'none';
                row.querySelectorAll('span')[0].textContent = product.name;
                row.querySelectorAll('span')[1].textContent = `$${product.price}`;
                row.querySelectorAll('span')[2].textContent = product.type;
                row.querySelectorAll('span')[3].textContent = product.quantity;
                row.querySelectorAll('span')[4].textContent = product.description;
            }
        });
    }

    function deleteProduct(productId, row) {
        fetch('/delete_product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: productId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Product deleted successfully!');
                row.remove();
            }
        });
    }

    function updateFAQ(faq, row) {
        fetch('/update_faq', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(faq),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('FAQ updated successfully!');
                row.classList.remove('edit-mode');
                row.classList.add('view-mode');
                row.querySelector('.edit-btn').style.display = 'inline-block';
                row.querySelector('.save-btn').style.display = 'none';
                row.querySelectorAll('span')[0].textContent = faq.question;
                row.querySelectorAll('span')[1].textContent = faq.answer;
                // Update the original faq object with the new question
                faq.question = faq.question;
            }
        });
    }


    function deleteFAQ(question, row) {
        fetch('/delete_faq', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('FAQ deleted successfully!');
                row.remove();
            }
        });
    }
    businessInfoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const businessInfo = {
            name: document.getElementById('business-name').value,
            description: document.getElementById('business-description').value,
            brandVoice: document.getElementById('brand-voice').value
        };
        fetch('/save_business_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(businessInfo),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Business information saved successfully!');
            }
        });
    });
    
});