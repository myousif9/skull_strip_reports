from nilearn import plotting
import nipype.interfaces.io as nio
import nipype.pipeline.engine as pe
from nipype import Node, Function, JoinNode, Workflow
from nipype.interfaces import utility as niu
import sys
import os

# Grabbing All beast skull stripped images

def pipeline_gen(beast_path,gradcorr_path,temp_path,subject):
    # Beast input node
    beast_input = Node(nio.DataGrabber(infields=['subject_id'],outfields=['beast_path']), name ='beast_input')
    beast_input.inputs.base_directory = beast_path # replace with sys.argv[1]
    beast_input.inputs.template = '%s/anat/s*_desc-BEAST_T1w_brain.nii.gz'
    beast_input.inputs.subject_id = subject
    beast_input.inputs.sort_filelist = True

    # gradient corrected image input node
    grad_input = Node(nio.DataGrabber(infields = ['subject_id'], outfields=['grad_path']), name='gradient_input')
    grad_input.inputs.base_directory = gradcorr_path
    grad_input.inputs.template = '%s/anat/s*_T1w.nii.gz'
    grad_input.inputs.subject_id = subject
    grad_input.inputs.sort_filelist = True

    # function for generating overlay of skull stripped and original image
    def gen_overlay(grad,beast,temp_path,subject_id):
        #importing function due to nipype necessity
        from nilearn import plotting
        import os

        # checks if data folder exists and if it does data folder is created
        # if os.path.exists(data) == False:
            # os.makedirs(data)

        # defining paths for overlay outputs
        out_file_x = os.path.join(temp_path,'{subject_id}-sagital.png'.format(subject_id =subject_id))
        out_file_y = os.path.join(temp_path,'{subject_id}-coronal.png'.format(subject_id = subject_id))
        out_file_z = os.path.join(temp_path,'{subject_id}-axial.png'.format(subject_id = subject_id))
        
        #generating overlay and saving 3 different axes of brain images
        plotting.plot_roi(beast, grad, alpha = 0.5, display_mode = 'x',output_file = out_file_x)
        plotting.plot_roi(beast, grad, alpha = 0.5, display_mode = 'y',output_file = out_file_y)
        plotting.plot_roi(beast, grad, alpha = 0.5, display_mode = 'z',output_file = out_file_z)
    
    # def subject_func(subject):
    #     return subject
    
    # subject_node = Node(name='subject_passer', interface(input))

    # overally node and inputing subject for function
    overlay_node = Node(name='gen_overlay', interface=Function(input_names = ['grad','beast','temp_path','subject_id'], output_name = [], function=gen_overlay))
    overlay_node.inputs.subject_id = subject
    overlay_node.inputs.temp_path = temp_path


    # generating overlay pipline
    pipeline = Workflow(name='overlay_pipeline')
    pipeline.connect([(beast_input,overlay_node, [('beast_path','beast')])])
    pipeline.connect([(grad_input,overlay_node, [('grad_path','grad')])])
    pipeline.run()

if __name__=='__main__':
    subject_list = []

    #parsing beast skull strip folder for subject list
    beast_path = '/home/myousif/graham/scratch/DM1_correct7t/beast_v0.0.2'
    grad_path = '/home/myousif/graham/scratch/DM1_correct7t/gradcorrect.simg'
    temp_path = '/home/myousif/graham/scratch/skull_strip_reports'
    for sub in os.listdir(beast_path):
        if 'sub' in sub:
            subject_list.append(sub)

    # for sub in subject_list:
    #     pipeline_gen(beast_path,grad_path,temp_path,sub)
    
    table_data = """
    <tr>
        <th>{sub}</th>
    </tr>
    <tr>
        <td><img src="{sub}-axial.png" </th>
    </tr>
    <tr>
        <td><img src="{sub}-sagital.png" </th>
    </tr>
    <tr>
        <td><img src="{sub}-crononal.png" </th>
    </tr>

    """
    with open('report.html','w+') as file:
        file.write('<html>')
        file.write('<body>')
        file.write('<h2> Skull Strip Reports')
        file.write('<table style="width:100%">')
        for sub in subject_list:
            file.write(table_data.format(sub='sub-S01'))
        file.write('</table>')
        file.write('</body>')
        file.write('</html>')


    


