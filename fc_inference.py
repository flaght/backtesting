# coding: utf-8

import tensorflow as tf
INPUT_NODE = 4 * 4
neurons_layer1 = 1024
neurons_layer2 = 512
neurons_layer3 = 256
neurons_layer4 = 128
n_target = 1


def chg_inference_regular(regularizes):
    with tf.variable_scope("", reuse=True):
        w1 = tf.get_variable("layer1/weight", [INPUT_NODE, neurons_layer1])
        w2 = tf.get_variable("layer2/weight", [neurons_layer1, neurons_layer2])
        w3 = tf.get_variable("layer3/weight", [neurons_layer2, neurons_layer3])
        w4 = tf.get_variable("layer4/weight", [neurons_layer3, neurons_layer4])
    return regularizes(w1) + regularizes(w2) + regularizes(w3) + regularizes(w4)


def chg_nn_layer(input_tensor, input_dim, out_dim, layer_name, monitor, avg_class=None,reuse=False, act=tf.nn.relu):

    with tf.variable_scope(layer_name):
        weights = tf.get_variable("weight", [input_dim, out_dim],
                                  initializer=tf.truncated_normal_initializer(stddev=0.1))
        if monitor != None:
            monitor.variable_summaries(layer_name + '/weights', weights)

        biases = tf.get_variable("biases", [out_dim], initializer=tf.constant_initializer(0.0))

        if monitor != None:
            monitor.variable_summaries(layer_name + '/biases', biases)

        if avg_class == None:
            preactive = tf.add(tf.matmul(input_tensor, weights), biases)
        else:
            preactive = tf.add(tf.matmul(input_tensor, avg_class.average(weights)) + avg_class.average(biases))

        if monitor != None:
            monitor.variable_summaries(layer_name + '/pre_activations', preactive)

        activations = act(preactive, name='activations')

        if monitor != None:
            monitor.variable_summaries(layer_name + '/activations', activations)
        return activations


def chg_inference(input_tensor, monitor, avg_class, reuse): #涨跌幅前向计算
    hidden1 = chg_nn_layer(input_tensor, INPUT_NODE, neurons_layer1,
                           'layer1', monitor,avg_class, reuse)

    hidden2 = chg_nn_layer(hidden1, neurons_layer1, neurons_layer2,
                           'layer2', monitor, avg_class, reuse)

    hidden3 = chg_nn_layer(hidden2, neurons_layer2, neurons_layer3,
                           'layer3', monitor, avg_class, reuse)

    hidden4 = chg_nn_layer(hidden3, neurons_layer3, neurons_layer4,
                           'layer4', monitor, avg_class, reuse)

    output = chg_nn_layer(hidden4, neurons_layer4, n_target,
                          'output', monitor, avg_class, reuse)
    return output


def per_chg_nn_layer(input_tensor, input_dim, out_dim, layer_name, monitor, avg_class=None,reuse=False, act=tf.nn.relu):

    weights = tf.Variable(tf.truncated_normal(shape=[input_dim,out_dim],
                                                         stddev=0.1))

    biases = tf.Variable(tf.constant(0.0,shape=[out_dim]))
    
    if avg_class == None:
        preactive = tf.add(tf.matmul(input_tensor, weights), biases)
    else:
        preactive = tf.add(tf.matmul(input_tensor, avg_class.average(weights)) + avg_class.average(biases))


    activations = act(preactive, name='activations')

    return activations


def per_chg_inference(input_tensor, monitor, avg_class, reuse): #涨跌幅前向计算
    hidden1 = per_chg_nn_layer(input_tensor, INPUT_NODE, neurons_layer1,
                           'layer1', monitor,avg_class, reuse)

    hidden2 = per_chg_nn_layer(hidden1, neurons_layer1, neurons_layer2,
                           'layer2', monitor, avg_class, reuse)

    hidden3 = per_chg_nn_layer(hidden2, neurons_layer2, neurons_layer3,
                           'layer3', monitor, avg_class, reuse)

    hidden4 = per_chg_nn_layer(hidden3, neurons_layer3, neurons_layer4,
                           'layer4', monitor, avg_class, reuse)

    output = per_chg_nn_layer(hidden4, neurons_layer4, n_target,
                          'output', monitor, avg_class, reuse)
    return output
