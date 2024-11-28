from flask import Flask, render_template, request, redirect, url_for
import hashlib
import os
import difflib

app = Flask(__name__)

# Function to calculate the file hash (SHA-256)
def calculate_hash(file_path, hash_type="sha256"):
    hash_func = hashlib.new(hash_type)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

# Function to calculate similarity percentage between two text files using difflib
def calculate_similarity(file1, file2):
    with open(file1, 'r', encoding='utf-8', errors='ignore') as f1, open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
        text1 = f1.read()
        text2 = f2.read()
    # Using difflib to get the ratio of similarity between two texts
    sequence_matcher = difflib.SequenceMatcher(None, text1, text2)
    return sequence_matcher.ratio() * 100  # Returns similarity as percentage

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare_hashes():
    reference_file = request.files['reference_file']
    student_file = request.files['student_file']

    if reference_file and student_file:
        ref_path = os.path.join('uploads', reference_file.filename)
        stu_path = os.path.join('uploads', student_file.filename)
        
        reference_file.save(ref_path)
        student_file.save(stu_path)

        # Calculate SHA256 hash of both files
        ref_sha256 = calculate_hash(ref_path, "sha256")
        stu_sha256 = calculate_hash(stu_path, "sha256")

        if ref_sha256 == stu_sha256:
            comparison_result = "Exact match (Plagiarism detected)"
            similarity_percentage = 100.0  # If the hashes are the same, the match is 100%
        else:
            # Calculate the similarity percentage of the content using difflib
            similarity_percentage = calculate_similarity(ref_path, stu_path)
            comparison_result = f"No exact match, but similarity is {similarity_percentage:.2f}%."

        return render_template('result.html', comparison_result=comparison_result, ref_sha256=ref_sha256, stu_sha256=stu_sha256, similarity_percentage=similarity_percentage)

    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
