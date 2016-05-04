import tensorflow as tf

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


def main():
    sess = tf.Session()

    x = tf.placeholder(tf.float32, [None, 784])  # training input
    x_image = tf.reshape(x, [-1,28,28,1])

    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])

    y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
    y_ = tf.placeholder(tf.float32, [None, 10])  # labels that we will input

    cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

    correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # Tensorboard summary logging
    tf.scalar_summary('mnist_accuracy', accuracy)
    merged = tf.merge_all_summaries()
    train_writer = tf.train.SummaryWriter('logs/train', sess.graph)
    test_writer  = tf.train.SummaryWriter('logs/test')

    sess.run(tf.initialize_all_variables())

    for i in range(2000):
        batch = mnist.train.next_batch(100)
        
        if i % 100 == 0:  # Record summaries and accuracy on next batch of training data
            summary, acc = sess.run([merged, accuracy],
                feed_dict={x:batch[0], y_: batch[1], keep_prob: 1.0})
            test_writer.add_summary(summary, i)
            print('Accuracy at step {}: {:.4f}'.format(i, acc))
        else: # Record train set summaries, and train
            summary, _ = sess.run([merged, train_step],
                feed_dict={x:batch[0], y_: batch[1], keep_prob: 0.5})
            train_writer.add_summary(summary, i)
            
            
    summary, acc = sess.run([merged, accuracy],
        feed_dict={x:mnist.test.images, y_:mnist.test.labels, keep_prob: 1.0})
    print("\nFinal Testing Accuracy: {:.4f}".format(acc))


if __name__ == '__main__':
    main()
