$(document).ready(function() {
    let categories = {};
    let currentEditingProductId = null;  // 定义 currentEditingProductId 变量

    checkLogin();
    fetchCategoriesAndFillDropdown();
    fetchCurrentUserInfo();

    function checkLogin() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/login';
        }
    }

    function fetchCurrentUserInfo() {
        const token = localStorage.getItem('access_token');

        fetch('http://127.0.0.1:8000/auth/users/me/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Token expired or invalid');
            }
            return response.json();
        })
        .then(data => {
            if (data && data.full_name) {
                $('#user-fullname').text(`Welcome, ${data.full_name}`);
            } else {
                console.error('Error: full_name is not defined in the response');
                localStorage.removeItem('access_token');
                window.location.href = '/login';
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        });
    }

    $('#logout-btn').click(function() {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    });

    function fetchCategoriesAndFillDropdown() {
        fetch('/categories/')
        .then(response => response.json())
        .then(data => {
            const categoryDropdown = $('#productCategory');
            categoryDropdown.empty();
            data.forEach(category => {
                categories[category.category_id] = category.category_name;
                categoryDropdown.append(`<option value="${category.category_id}">${category.category_name}</option>`);
            });
            fetchProducts(); // 在加载分类信息后再加载产品信息
        })
        .catch(error => console.error('Error fetching categories:', error));
    }

    $('#saveProductBtn').click(function() {
        let formData = {
            product_category_id: parseInt($('#productCategory').val()),
            product_name: $('#productName').val(),
            product_specification: $('#productSpecification').val(),
            product_price: parseFloat($('#productPrice').val()),
            product_description: $('#productDescription').val(),
            product_parameters: $('#productParameters').val(),
            product_image: $('#productImageUrl').val()
        };

        console.log(formData);

        let method = currentEditingProductId ? 'PUT' : 'POST';
        let apiEndpoint = currentEditingProductId ? `/products/${currentEditingProductId}` : '/products/';

        fetch(apiEndpoint, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            $('#productModal').modal('hide');
            $('body').removeClass('modal-open');
            $('.modal-backdrop').remove();
            fetchProducts();
            currentEditingProductId = null;
            resetProductForm();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    function fetchProducts() {
        fetch('/products/')
        .then(response => response.json())
        .then(data => {
            const tableBody = $('#productsTable tbody');
            tableBody.empty();
            data.forEach(product => {
                let row = $('<tr></tr>');
                row.append(`<td>${product.product_id}</td>`);
                // 根据 product_category_id 查找分类名称
                const categoryName = categories[product.product_category_id] || '未分类';
                row.append(`<td>${categoryName}</td>`);
                row.append(`<td>${product.product_name}</td>`);
                row.append(`<td>${product.product_specification}</td>`);

                let actionsCell = $('<td></td>');
                let editButton = $('<button class="btn btn-info btn-sm">编辑</button>');
                let deleteButton = $('<button class="btn btn-danger btn-sm ml-2">删除</button>');  // 单引号修正

                editButton.click(function() {
                    currentEditingProductId = product.product_id;
                    $('#productCategory').val(product.product_category_id);
                    $('#productName').val(product.product_name);
                    $('#productSpecification').val(product.product_specification);
                    $('#productPrice').val(product.product_price);
                    $('#productDescription').val(product.product_description);
                    $('#productParameters').val(product.product_parameters);

                    if (product.product_image) {
                        $('#productImageUrl').val(product.product_image);
                        $('#productImagePreview').attr('src', product.product_image).show();
                    } else {
                        $('#productImageUrl').val('');
                        $('#productImagePreview').hide();
                    }

                    $('#productModal').modal('show');
                });

                deleteButton.click(function() {
                    if (confirm('确定要删除这个产品吗？')) {
                        fetch(`/products/${product.product_id}`, {
                            method: 'DELETE',
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Network response was not ok');
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log('Product deleted successfully:', data);
                            fetchProducts();
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                    }
                });

                actionsCell.append(editButton);
                actionsCell.append(deleteButton);
                row.append(actionsCell);
                tableBody.append(row);
            });
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    $('#productModal').on('show.bs.modal', function (e) {
        fetchCategoriesAndFillDropdown();
    });

    $('#productModal').on('hidden.bs.modal', function (e) {
        resetProductForm();
    });

    function resetProductForm() {
        $('#product-form')[0].reset();
        $('#productImagePreview').hide();
        $('#productImageUrl').val('');
        $('.progress').hide();
        $('.progress-bar').css('width', '0%').attr('aria-valuenow', 0);
    }

    document.getElementById('productImage').addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (!file) {
            console.error('No file selected.');
            return;
        }

        let formData = new FormData();
        formData.append('file', file);

        $('.progress').show();

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload/', true);

        xhr.upload.onprogress = function(event) {
            if (event.lengthComputable) {
                const percentComplete = Math.round((event.loaded * 100) / event.total);
                $('.progress-bar').css('width', percentComplete + '%').attr('aria-valuenow', percentComplete);
            }
        };

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                const data = JSON.parse(xhr.responseText);
                if (data.image_url) {
                    document.getElementById('productImageUrl').value = data.image_url;
                    document.getElementById('productImagePreview').src = data.image_url;
                    document.getElementById('productImagePreview').style.display = 'block';
                } else {
                    console.error('No image_url in response');
                }
            } else {
                console.error('Failed to upload image');
            }

            $('.progress').hide();
            $('.progress-bar').css('width', '0%').attr('aria-valuenow', 0);
        };

        xhr.onerror = function() {
            console.error('Error uploading image');
            $('.progress').hide();
            $('.progress-bar').css('width', '0%').attr('aria-valuenow', 0);
        };

        xhr.send(formData);
    });
});