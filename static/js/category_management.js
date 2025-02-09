document.addEventListener('DOMContentLoaded', function() {
    fetchCategories();
    fetchCurrentUserInfo();
});

function fetchCurrentUserInfo() {
    const token = localStorage.getItem('access_token'); // 假设令牌存储在localStorage中

    fetch('http://127.0.0.1:8000/auth/users/me/', { // 确保使用你的后端API端点
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token // 添加认证头部
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('creator').value = data.full_name; // 用返回的full_name填充
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


document.getElementById('addCategoryBtn').addEventListener('click', function(e) {
    e.preventDefault();
    const categoryName = document.getElementById('categoryName').value;
    const creator = document.getElementById('creator').value;

    fetch('/categories/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            category_name: categoryName,
            creator: creator,
            category_status: true
        })
    })
    .then(response => response.json())
    .then(data => {
        fetchCategories(); // 重新加载分类列表
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

function fetchCategories() {
    fetch('/categories/')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('categoriesTable').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';
        data.forEach(category => {
            let row = tableBody.insertRow();
            row.insertCell(0).innerText = category.category_id;
            row.insertCell(1).innerText = category.category_name;
            row.insertCell(2).innerText = category.category_status ? '激活' : '隐藏';
            row.insertCell(3).innerText = category.creator;
            let actionsCell = row.insertCell(4);

            let editButton = document.createElement('button');
            editButton.innerText = '编辑';
            editButton.className = 'btn btn-primary btn-sm';
            editButton.setAttribute('data-id', category.category_id); // 设置分类ID为按钮的数据属性
            editButton.onclick = function() { editCategory(this.getAttribute('data-id')); }; // 绑定点击事件处理函数
            actionsCell.appendChild(editButton);

            let deleteButton = document.createElement('button');
            deleteButton.innerText = '删除';
            deleteButton.className = 'btn btn-danger btn-sm';
            deleteButton.onclick = function() { deleteCategory(category.category_id); };
            actionsCell.appendChild(deleteButton);
        });
    });
}

function editCategory(categoryId) {
    fetch(`/categories/${categoryId}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('edit-category-name').value = data.category_name;
        document.getElementById('edit-category-status').value = data.category_status.toString();
        $('#editCategoryModal').modal('show'); // 使用jQuery显示模态框
        $('#save-category-changes').data('id', categoryId); // 将分类ID存储在保存按钮的数据属性中
    })
    .catch(error => console.error('Error:', error));
}

function deleteCategory(categoryId) {
    fetch(`/categories/${categoryId}`, {
        method: 'DELETE'
    })
    .then(() => {
        fetchCategories(); // 重新加载分类列表
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function updateCategory(categoryId, newName) {
    fetch(`/categories/${categoryId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('access_token') // 添加认证头部
        },
        body: JSON.stringify({
            category_name: newName
        })
    })
    .then(response => {
        if (response.ok) {
            fetchCategories(); // 更新成功后重新加载分类列表
        } else {
            alert('更新分类失败');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

$('#save-category-changes').click(function() {
    const categoryId = $(this).data('id'); // 从保存按钮的数据属性中获取分类ID
    const categoryName = $('#edit-category-name').val();
    const categoryStatus = $('#edit-category-status').val() === 'true';

    fetch(`/categories/${categoryId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('access_token') // 添加认证头部
        },
        body: JSON.stringify({
            category_name: categoryName,
            category_status: categoryStatus
        })
    })
    .then(response => {
        if (response.ok) {
            $('#editCategoryModal').modal('hide'); // 隐藏模态框
            fetchCategories(); // 重新加载分类列表
        } else {
            alert('更新分类失败');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});