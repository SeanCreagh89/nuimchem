var previous;

function dropdownmenu(menu) {
	var current = document.getElementById(menu);
	var last = document.getElementById(previous);

	if (previous == menu) {
		if (last.style.display == 'block') {
			last.style.display = 'none';
		} else {
			last.style.display = 'block';
		}
		last = null;
	} else if (current.style.display == 'block') {
		current.style.display = 'none';
		previous = menu;
	} else {
		current.style.display = 'block';
		previous = menu;
	}

	if (last != null) {
		last.style.display = 'none';
	}
}

function dropdownlist(main, sub) {
	var main = document.getElementById(main);
	var sub = document.getElementById(sub);
	sub.innerHTML = "";

	if (main.value == "please select primary location") {
		var option = ["please choose from above|please choose from above"];
	} else if (main.value == "Main Stores") {
		var option = ["please select sub location|please select sub location", "Corrosives|Corrosives", "Explosives|Explosives", "Flammable|Flammable", "Freezer|Freezer", "Fridge 1|Fridge 1", "Fridge 2|Fridge 2", "General Use Solvents|General Use Solvents", "Miscellaneous Dangerous Goods|Miscellaneous Dangerous Goods", "NMR/HPLC Solvents|NMR/HPLC Solvents", "Non Classified|Non Classified", "Oxidising|Oxidising", "S Block Metals Chest|S Block Metals Chest", "Silica Drum|Silica Drum", "Toxic|Toxic"];
	} else if (main.value == "1st Year Lab 1.39") {
		var option = ["please select sub location|please select sub location", "Fumehood 21|Fumehood 21", "Fumehood 22|Fumehood 22", "Fumehood 23|Fumehood 23", "Fumehood 24|Fumehood 24", "Fumehood 25|Fumehood 25"];
	} else if (main.value == "3rd Year Lab") {
		var option = ["please select sub location|please select sub location", "Barbara|Barbara", "Fumehood 13|Fumehood 13", "Fumehood 14|Fumehood 14", "Fumehood 15|Fumehood 15", "Fumehood 16|Fumehood 16", "Fumehood 17|Fumehood 17", "Fumehood 18|Fumehood 18", "Fumehood 19|Fumehood 19", "Fumehood 20|Fumehood 20", "Prep Room|Prep Room"];
	} else if (main.value == "Bio-Analytics Lab (1.59)") {
		var option = ["please select sub location|please select sub location", "Auxilla Lab|Auxilla Lab", "Callan Lab|Callan Lab", "Fridge|Fridge", "Fiachra|Fiachra", "John Kealy|John Kealy", "Keeley|Keeley", "Maryanne|Maryanne", "Michelle|Michelle", "Niall|Niall"];
	} else if (main.value == "Biophysical Lab (1.53)") {
		var option = ["please select sub location|please select sub location", "Freezer|Freezer", "Fridge|Fridge"];
	} else if (main.value == "Biophysical Lab 2") {
		var option = ["please select sub location|please select sub location", "Freezer|Freezer", "Fridge|Fridge", "Alice|Alice", "Jennifer|Jennifer", "Mark|Mark", "Michelle|Michelle", "Ruth|Ruth", "Susan|Susan", "Urzula|Urzula"];
	} else if (main.value == "Electrochemistry Lab (1.55)") {
		var option = ["please select sub location|please select sub location", "Carmel|Carmel", "David|David", "Karen|Karen", "Paul|Paul"];
	} else if (main.value == "Francis Lab") {
		var option = ["please select sub location|please select sub location", "Fridge|Fridge", "Lab|Lab"];
	} else if (main.value == "Low Temperature Lab (1.58)") {
		var option = ["please select sub location|please select sub location", "Fridge|Fridge", "Barry|Barry", "Chris|Chris", "Sean|Sean"];
	} else if (main.value == "Natasha Lab") {
		var option = ["please select sub location|please select sub location", "Emer|Emer", "Manfredi|Manfredi"];
	} else if (main.value == "Physical Chemistry Lab 1.42") {
		var option = ["please select sub location|please select sub location", "Fumehood|Fumehood", "Chromatography_Barbara|Chromatography_Barbara", "Dry Chemicals 1|Dry Chemicals 1", "Dry Chemicals 2|Dry Chemicals 2", "Shelf 17|Shelf 17", "Shelf 18|Shelf 18", "Shelf 19|Shelf 19", "Shelf 21|Shelf 21", "Shelf 22|Shelf 22"];
	} else if (main.value == "Prep Room 1.41") {
		var option = ["please select sub location|please select sub location", "Main Shelf|Main Shelf", "Fumehood|Fumehood"];
	} else if (main.value == "Synthesis Lab (2.52)") {
		var option = ["please select sub location|please select sub location", "Adam|Adam", "Andrew|Andrew", "Colette|Colette", "Denise|Denise", "Francis|Francis", "Jack|Jack", "Jessica|Jessica", "John McGinley|John McGinley", "John Stephens|John Stephens", "John Walsh|John Walsh", "Justine|Justine", "Malachy|Malachy", "Pauric|Pauric", "Ross|Ross", "Sam|Sam", "Triny|Triny", "Ursula|Ursula"];
	} else {
		var option = ["no sub locations exist|no sub locations exist"];
	}

	for (var o in option) {
		var pair = option[o].split("|");
		var newOption = document.createElement("option");
		newOption.value = pair[0];
		newOption.innerHTML = pair[1];
		sub.options.add(newOption);
	}
}

function dropdownwaste(main, sub) {
	var main = document.getElementById(main);
	var sub = document.getElementById(sub);
	sub.innerHTML = "";

	if (main.value == "please select primary location") {
		var option = ["please select sub location|please select sub location"];
	} else if (main.value == "Main Stores") {
		var option = ["please select sub location|please select sub location", "Waste Cabinet|Waste Cabinet"];
	} else {
		var option = ["no sub locations exist|no sub locations exist"];
	}

	for (var o in option) {
		var pair = option[o].split("|");
		var newOption = document.createElement("option");
		newOption.value = pair[0];
		newOption.innerHTML = pair[1];
		sub.options.add(newOption);
	}
}

function hiddenclass(current, next) {
	var current = document.getElementById(current);
	var next = document.getElementById(next);

	var class2 = document.getElementById("classification2");
	var class3 = document.getElementById("classification3");
	var class4 = document.getElementById("classification4");
	var class5 = document.getElementById("classification5");
	var class6 = document.getElementById("classification6");

	if (current.value == "please select classification") {
		next.style.display = 'none';
		class3.style.display = 'none';
		class4.style.display = 'none';
		class5.style.display = 'none';
		class6.style.display = 'none';
	} else if (current.value == "please select a second classification") {
		next.style.display = 'none';
		class4.style.display = 'none';
		class5.style.display = 'none';
		class6.style.display = 'none';
	} else if (current.value == "please select a third classification") {
		next.style.display = 'none';
		class5.style.display = 'none';
		class6.style.display = 'none';
	} else if (current.value == "please select a fourth classification") {
		next.style.display = 'none';
		class6.style.display = 'none';
	} else if (current.value == "please select a fifth classification") {
		next.style.display = 'none';
	} else {
		next.style.display = 'block';
	}
}

function counter(field, count, limit) {
	var remaining = document.getElementById(count);

	if (field.value.length > limit)
		field.value = field.value.substring(0, limit);
	else
		remaining.value = limit - field.value.length;
}

function printreport(report) {
	var restorepage = document.body.innerHTML;
	var printcontent = document.getElementById(report).innerHTML;
	document.body.innerHTML = printcontent;
	window.print();
	document.body.innerHTML = restorepage;
}