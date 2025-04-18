document.addEventListener('DOMContentLoaded', function() {
    // Initialize sortable for each question list
    document.querySelectorAll('.sortable-questions').forEach(function(el) {
        new Sortable(el, {
            animation: 150,
            handle: '.drag-handle',
            onEnd: function(evt) {
                const questionId = evt.item.getAttribute('data-id');
                const newOrder = evt.newIndex + 1;
                const stageId = evt.item.closest('.question-stage').getAttribute('data-stage-id');
                
                // Send AJAX request to update the order
                const form = new FormData();
                form.append('question_id', questionId);
                form.append('new_order', newOrder);
                form.append('stage_id', stageId);
                
                fetch('/admin/recruitment/question/reorder/', {
                    method: 'POST',
                    body: form,
                    headers: {
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Update displayed numbers
                        updateQuestionNumbers(evt.item.closest('.question-stage'));
                    } else {
                        alert('Error updating question order: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while updating the question order.');
                });
            }
        });
    });
    
    // Function to update question numbers after reordering
    function updateQuestionNumbers(stageElement) {
        const questions = stageElement.querySelectorAll('.question-item');
        questions.forEach((question, index) => {
            question.querySelector('.question-number').textContent = index + 1;
        });
    }
    
    // Function to get CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Sync to Google Sheets button
    document.getElementById('sync-to-sheets-btn').addEventListener('click', function(e) {
        e.preventDefault();
        
        const btn = this;
        btn.disabled = true;
        btn.textContent = 'Syncing...';
        
        fetch('/admin/recruitment/question/sync-to-sheets/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            btn.disabled = false;
            btn.textContent = 'Sync to Google Sheets';
            
            if (data.status === 'complete') {
                alert('Questions successfully synced to Google Sheets');
            } else {
                alert('Error syncing questions: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            btn.disabled = false;
            btn.textContent = 'Sync to Google Sheets';
            alert('An error occurred while syncing questions to Google Sheets.');
        });
    });
});