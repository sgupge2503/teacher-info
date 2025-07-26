const API_BASE_URL = 'http://127.0.0.1:8000/api';

// 全教員データを保持する変数
let allTeachers = [];

// パスの末尾に応じて処理を振り分ける
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.endsWith('detail.html')) {
        renderDetailPage();
    } else {
        initIndexPage();
    }
});

// 一覧ページの初期化
async function initIndexPage() {
    try {
        const response = await fetch(`${API_BASE_URL}/teachers`);
        if (!response.ok) throw new Error('Failed to fetch teachers');
        allTeachers = await response.json();
        
        // 初期表示
        renderTeacherList(allTeachers);

        // 検索ボックスのイベントリスナーを設定
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.toLowerCase();
            const filteredTeachers = allTeachers.filter(teacher => 
                teacher.name.toLowerCase().includes(searchTerm) || 
                (teacher.ruby && teacher.ruby.toLowerCase().includes(searchTerm))
            );
            renderTeacherList(filteredTeachers);
        });

    } catch (error) {
        console.error('Error initializing index page:', error);
        document.getElementById('teacher-grid').innerHTML = '<p>教員情報の読み込みに失敗しました。</p>';
    }
}

// 教員リストをレンダリングする関数
function renderTeacherList(teachers) {
    const grid = document.getElementById('teacher-grid');
    grid.innerHTML = ''; // 表示をクリア

    if (teachers.length === 0) {
        grid.innerHTML = '<p>該当する教員が見つかりません。</p>';
        return;
    }

    teachers.forEach(teacher => {
        const card = document.createElement('div');
        card.className = 'teacher-card';
        const image = teacher.image ? `images/${teacher.image.split('/').pop()}` : 'images/noimage.png';
        
        card.innerHTML = `
            <a href="detail.html?id=${teacher.id}">
                <img src="${image}" alt="${teacher.name}" class="teacher-image">
                <div class="teacher-info">
                    <h4>${teacher.name}</h4>
                    ${teacher.ruby ? `<p class="ruby">${teacher.ruby}</p>` : ''}
                </div>
            </a>
        `;
        grid.appendChild(card);
    });
}

// 詳細ページをレンダリング
async function renderDetailPage() {
    const params = new URLSearchParams(window.location.search);
    const teacherId = params.get('id');
    if (!teacherId) {
        window.location.href = '/';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/teacher/${teacherId}`);
        if (!response.ok) throw new Error('Failed to fetch teacher details');
        const data = await response.json();
        
        const { teacher, basic_info, keywords, areas, papers } = data;

        document.title = `${teacher.name} - 教員詳細`;
        document.getElementById('teacher-name-title').textContent = `${teacher.name} の詳細情報`;

        const profileContent = document.getElementById('teacher-profile-content');
        const image = teacher.image ? `images/${teacher.image.split('/').pop()}` : 'images/noimage.png';

        profileContent.innerHTML = `
            <div class="teacher-profile">
                <div class="profile-header">
                    <img src="${image}" alt="${teacher.name}" class="profile-image">
                    <div class="profile-info">
                        <h2>${teacher.name}</h2>
                        ${teacher.ruby ? `<p class="ruby">${teacher.ruby}</p>` : ''}
                        <p class="url"><a href="${teacher.url}" target="_blank">${teacher.url}</a></p>
                    </div>
                </div>

                ${basic_info.length > 0 ? `
                <section class="basic-info">
                    <h3>基本情報</h3>
                    <table class="info-table">
                        ${basic_info.map(info => `<tr><th>${info.key}</th><td>${info.value}</td></tr>`).join('')}
                    </table>
                </section>` : ''}

                ${keywords.length > 0 ? `
                <section class="keywords">
                    <h3>研究キーワード</h3>
                    <div class="keyword-list">
                        ${keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}
                    </div>
                </section>` : ''}

                ${areas.length > 0 ? `
                <section class="research-areas">
                    <h3>研究分野</h3>
                    <table class="areas-table">
                        <thead><tr><th>研究分野</th></tr></thead>
                        <tbody>${areas.map(area => `<tr><td>${area}</td></tr>`).join('')}</tbody>
                    </table>
                </section>` : ''}

                ${papers.length > 0 ? `
                <section class="papers">
                    <h3>主要論文</h3>
                    <table class="papers-table">
                        <thead><tr><th>論文タイトル</th></tr></thead>
                        <tbody>
                            ${papers.map(paper => `<tr><td><a href="${paper.link}" target="_blank">${paper.title}</a></td></tr>`).join('')}
                        </tbody>
                    </table>
                </section>` : ''}
            </div>
        `;
    } catch (error) {
        console.error('Error rendering detail page:', error);
        document.getElementById('teacher-profile-content').innerHTML = '<p>教員詳細の読み込みに失敗しました。</p>';
    }
}
