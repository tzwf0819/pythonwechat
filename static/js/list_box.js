document.addEventListener('DOMContentLoaded', async function() {
    try {
        // 1. 从后端获取菜单数据
        const menuData = await fetchMenuItems('http://127.0.0.1:8000/items/');
        const menuTree = buildMenuTree(menuData);
        const menuHtml = generateMenuHtml(menuTree);

        // 2. 将生成的HTML设置到侧边栏容器
        document.getElementById('sidebar-menu').innerHTML = menuHtml;

        // 3. 初始化侧边栏宽度调整功能
        initResizeHandle();

        // 4. 初始化菜单展开/折叠功能
        initMenuToggle();
    } catch (error) {
        console.error('Error fetching menu items:', error);
    }
});

async function fetchMenuItems(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}
function buildMenuTree(items, parentCode = '0-0-0') {
    return items
        .filter(item => {
            // 直接子菜单的判断逻辑：父菜单Code与子菜单Code第一段相同，且子菜单Code第二段不为0
            const itemParts = item.hierarchy_code.split('-');
            const parentParts = parentCode.split('-');
            return itemParts[0] === parentParts[0] && (parentCode === '0-0-0' || itemParts[1] !== '0');
        })
        .map(item => ({
            ...item,
            // 递归构建子菜单，传入当前项的hierarchy_code作为下一轮的parentCode
            children: buildMenuTree(items, item.hierarchy_code)
        }));
}

function getNextLevelHierarchy(hierarchy_code) {
    let parts = hierarchy_code.split('-').map(Number);
    if (parts[1] === 0 && parts[2] === 0) { // It's a top-level item
        return `${parts[0]}-`;
    } else if (parts[2] === 0) { // It's a second-level item
        return `${parts[0]}-${parts[1]}-`;
    } else { // For deeper levels, you might need to adjust this
        return hierarchy_code; // This example does not fully account for deeper levels
    }
}

function generateMenuHtml(menuItems) {
    let html = '<ul class="menu-list">';
    for (const item of menuItems) {
        html += `<li class="menu-item${item.children && item.children.length ? ' has-children' : ''}">`;
        html += `<span class="menu-toggle">${item.name}</span>`;
        if (item.children && item.children.length) {
            // 递归调用来生成子菜单的HTML
            html += `<div class="sub-menu">${generateMenuHtml(item.children)}</div>`;
        }
        html += '</li>';
    }
    html += '</ul>';
    return html;
}


// 初始化侧边栏宽度调整功能
function initResizeHandle() {
    const sidebar = document.getElementById('sidebar-menu');
    const handle = document.createElement('div');
    handle.className = 'resize-handle';
    sidebar.appendChild(handle);

    let isResizing = false;
    let lastX = 0;

    handle.addEventListener('mousedown', function(e) {
        isResizing = true;
        lastX = e.clientX;
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', stopResize);
    });

    function handleMouseMove(e) {
        if (!isResizing) return;
        const dx = e.clientX - lastX;
        const newWidth = parseInt(getComputedStyle(sidebar).width, 10) + dx;
        sidebar.style.width = `${newWidth}px`;
        lastX = e.clientX;
    }

    function stopResize() {
        isResizing = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', stopResize);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 添加事件监听到所有的菜单切换元素
    document.querySelectorAll('.menu-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const subMenu = toggle.nextElementSibling;
            if (subMenu && subMenu.classList.contains('sub-menu')) {
                // 切换子菜单的显示状态
                subMenu.style.display = subMenu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
});

function initMenuToggle() {
    document.querySelectorAll('.menu-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const subMenu = toggle.nextElementSibling;
            if (subMenu && subMenu.classList.contains('sub-menu')) {
                subMenu.style.display = subMenu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
}