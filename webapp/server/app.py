from flask import Flask, request, send_file, jsonify
import torch
from torchvision.transforms import transforms
from PIL import Image
import io
from models import GeneratorResNet
import glob




# Initialize Flask app
app = Flask(__name__)


@app.route('/',methods=['GET'])
def hello():
   d = glob.glob("/content/*.*")
   return f"<p>hello world</p>"
@app.route('/process-image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400

    try:
      
        input_shape = (3,256,245)
        n_residual_blocks = 9
        transforms_ = [ transforms.ToTensor(),
                        transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5)) ]
        preprocess = transforms.Compose(transforms_)
        postprocess = transforms.ToPILImage()
        model = GeneratorResNet(input_shape,n_residual_blocks)
        model.load_state_dict(torch.load("../../G_BA_state_dict_final.pth",map_location=torch.device("cpu")))
       
        model.eval()
        img = Image.open(file.stream).convert('RGB')
        img = preprocess(img)
        img = img.unsqueeze(0)

        with torch.no_grad():

            output = 0.5 *  (model(img).data + 1.0)

        output_img = output.squeeze(0)
        output_img = postprocess(output_img)
        # Save the image to a BytesIO object
        img_io = io.BytesIO()
        output_img.save(img_io, 'png')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__" : 
       app.run()


