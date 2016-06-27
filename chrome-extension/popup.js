document.addEventListener('DOMContentLoaded', function() {
	console.log('loaded');
	var checkPageButton = document.getElementById('checkPage');
	checkPageButton.addEventListener('click', function() {
		chrome.tabs.getSelected(null, function(tab) {
			d = document;
			var f = d.createElement('form');
			f.action = 'http://library.frontyardprojects.org/trover';
			f.method = 'post';
			var i = d.createElement('input');
			i.type = 'hidden';
			i.name = 'trovelink';
			i.value = tab.url;
			f.appendChild(i);
			d.body.appendChild(f);
			f.submit();
		});
	}, false);
}, false);