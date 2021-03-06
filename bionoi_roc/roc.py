'''
    Process the .json file generated by transfer_learning_cnn_cv.py.
    It generates:
        1. average training/validating accuracy over the 10 folds when picking
           the epoch with the best MCC.
        2. average training/validating MCC over the 10 folds when picking the epoch
           with the best validation MCC.
        3. the ROC curve of the 10 folds when picking the epoch with the best validation MCC.
        4. the mean ROC curve of the 10 folds.
'''
import numpy as np
import pickle
from scipy import interp
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import json
import matplotlib.pyplot as plt
from statistics import mean 
import argparse

def getArgs():
    parser = argparse.ArgumentParser('python')
    parser.add_argument('-op',
                        default='control_vs_heme',
                        required=False,
                        choices = ['control_vs_heme', 'control_vs_nucleotide'],
                        help='Operation mode, control_vs_heme, or control_vs_nucleotide')
    return parser.parse_args()


def ror_plot(result_dir, model_name, color, dashes, title):
    with open(result_dir) as fp:
        loaded_file = json.load(fp)
    roc_list = loaded_file['roc']
    k = len(roc_list) # number of folds
    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)

    for i in range(k):
        roc_dict = roc_list[i]
        fpr = roc_dict['fpr']
        tpr = roc_dict['tpr']
        thresholds = roc_dict['thresholds']
        tprs.append(interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        #plt.plot(fpr, tpr, lw=1, alpha=0.3,label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    print('Averaged AUC for {}: {}'.format(model_name, mean_auc))
    std_auc = np.std(aucs)
    plt.plot(mean_fpr, mean_tpr, dashes=dashes, color=color, label=model_name, lw=2, alpha=.8)



if __name__ == "__main__":
    # get the operation mode: control_vs_heme or control_vs_nucleotide
    args = getArgs()
    op = args.op
    print('roc plots for ' + op)
    plt.rcParams.update({'font.size': 19})
    plt.rcParams.update({"font.family": "sans-serif"})

    if op == 'control_vs_heme':
        title = '(b)'
        cnn_dir = '../bionoi_cnn_homology_reduced/results/control_vs_heme_cv_9thrun.json'
        mlp_img_dir = '../bionoi_ml_homology_reduced/mlp_img_result/control_vs_heme_cv_1th_run.json'
        mlp_autoencoder_vec_dir = '../bionoi_ml_homology_reduced/mlp_autoencoder_vec_result/control_vs_heme_cv_1th_run.json'
        rf_autoencoder_vec_dir = '../bionoi_ml_homology_reduced/rf_autoencoder_vec_result/control_vs_heme_cv_6th_run.json'
    elif op == 'control_vs_nucleotide':
        cnn_dir = '../bionoi_cnn_homology_reduced/results/control_vs_nucleotide_cv_12thrun.json'
        mlp_img_dir = '../bionoi_ml_homology_reduced/mlp_img_result/control_vs_nucleotide_cv_1th_run.json'
        mlp_autoencoder_vec_dir = '../bionoi_ml_homology_reduced/mlp_autoencoder_vec_result/control_vs_nucleotide_cv_1th_run.json'
        rf_autoencoder_vec_dir = '../bionoi_ml_homology_reduced/rf_autoencoder_vec_result/control_vs_nucleotide_cv_6th_run.json'
        title = '(a)'

    dirs = [cnn_dir, mlp_img_dir, mlp_autoencoder_vec_dir, rf_autoencoder_vec_dir]
    model_names = ['BionoiNet', 'Flat/MLP', 'Autoencoder/MLP', 'Autoencoder/RF']
    colors = ['blue', 'red', 'magenta', 'limegreen']
    dashes_list = ['', [6, 1, 1, 1], [6, 1, 1, 1, 1, 1], [6, 1, 1, 1, 1, 1, 1, 1]]
    
    fig=plt.figure(figsize=(10, 10))
    plt.tight_layout()
    
    for i in range(4):
        ror_plot(result_dir=dirs[i], model_name=model_names[i], color=colors[i], dashes=dashes_list[i], title=title)

    plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='slategrey',label='Random', alpha=.8)

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")

    if op == 'control_vs_heme':
        plt.savefig('./b.png', bbox_inches = 'tight', dpi=600)
    elif op == 'control_vs_nucleotide':
        plt.savefig('./a.png', bbox_inches = 'tight', dpi=600)
    plt.show()