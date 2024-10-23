const textBoxList = document.getElementsByClassName('list-inline');

for (let i = 0; i < textBoxList.length; i++) {
    const buttonEdit = textBoxList[i].querySelector('.fa-pen-to-square');
    const showLocker = textBoxList[i].querySelector('.show-locker'); 
    const editLocker = textBoxList[i].querySelector('.edit-locker'); 

    buttonEdit.addEventListener('click', function() {
        if (showLocker.style.display === 'none') {
            showLocker.style.display = 'flex'; 
            editLocker.style.display = 'none';   
        } else {
            showLocker.style.display = 'none';   
            editLocker.style.display = 'flex';  
        }
    });
}
