$(document).ready(function() {
    // 加载产品列表
    fetchProducts();

    // 处理保存产品按钮点击事件
    $('#saveProductBtn').click(function() {
        const productName = $('#productName').val();
        const productSpecification = $('#productSpecification').val();
        const productPrice = $('#productPrice').val();
        const productDescription = $('#productDescription').val();

        // 发送请求添加产品
        fetch('/products/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_name: productName,
                product_specification: productSpecification,
                product_price: productPrice,
                product_description: productDescription
            })
        })
        .then(response => response.json())
        .then(data => {
            $('#productModal').modal('hide'); // 隐藏模态框
            fetchProducts(); // 重新加载产品列表
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});

function fetchProducts() {
    fetch('/products/')
    .then(response => response.json())
    .then(data => {
        const tableBody = $('#productsTable tbody');
        tableBody.empty(); // 清空表格体
        data.forEach(product => {
            tableBody.append(`
                <tr>
                    <td>${product.product_id}</td>
                    <td>${product.product_name}</td>
                    <td>${product.product_specification}</td>
                    <td>${product.product_price}</td>
                    <td>${product.product_description}</td>
                    <td>
                        <!-- 在这里添加编辑和删除按钮 -->
                    </td>
                </tr>
            `);
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}