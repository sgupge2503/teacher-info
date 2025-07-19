// 教員選択時の自動遷移機能
document.addEventListener('DOMContentLoaded', function() {
    const teacherSelect = document.getElementById('teacher_id');
    
    if (teacherSelect) {
        // セレクトボックスの変更時に自動で詳細ページに遷移
        teacherSelect.addEventListener('change', function() {
            if (this.value) {
                window.location.href = `/teacher/${this.value}`;
            }
        });
    }
    
    // 教員カードのホバー効果
    const teacherCards = document.querySelectorAll('.teacher-card');
    teacherCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-2px)';
        });
    });
    
    // 論文リンクの外部リンク警告
    const paperLinks = document.querySelectorAll('.paper-link');
    paperLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.hostname !== window.location.hostname) {
                const confirmed = confirm('外部サイトに移動します。よろしいですか？');
                if (!confirmed) {
                    e.preventDefault();
                }
            }
        });
    });
    
    // キーワードタグのクリック機能（将来の拡張用）
    const keywordTags = document.querySelectorAll('.keyword-tag');
    keywordTags.forEach(tag => {
        tag.addEventListener('click', function() {
            console.log('Clicked keyword:', this.textContent);
            // 将来的にキーワード検索機能を実装する場合はここに追加
        });
    });
});
