def tagging():

	classes = db.get_classes()
	class_names = [ class_name for class_name,id in classes ]
	class_names.remove('none')

	print(class_names)
	query = "SELECT face_path FROM untagged_images"
	cursor.execute(query)
	images = cursor.fetchall()

	divs =[]
	for i in images:
		divs.append(
			f"""
			<div class="brick">
			<img src="static/{i[0]}" alt="{os.path.basename(i[0])}">
			</div>
			"""
		)

	divs = "\n".join(divs)

	return render_template('tagging.html')