/**
 * File: flooder.c
 *
 * Description   : Traffic source for sdnlb.
 * Created By    : Quinn Burke (qkb5007@psu.edu)
 * Date          : January 2020
 * Last Modified : January 2020
 */

/* Include Files  */
#include <pcap.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdbool.h>

#include <sys/socket.h>
#include <arpa/inet.h>

#include <netdb.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include <net/if.h>
#include <netinet/ether.h>

#include <unistd.h>

#include <pthread.h>

/* Project Includes  */

/* Definitions  */
struct pkt_node
{
    u_char *eth_pkt;
    int length;
    // struct pkt_node *next;
};

struct active_flow
{
    struct pkt_node *pnode; // rate of flow is just the pkt size (the avg rate)
    int duration;
    int time_active;
    time_t start_time;
};

struct active_flow_node_t
{
    struct active_flow *af;
    struct active_flow_node_t *next;
    struct active_flow_node_t *prev;
} * head;

void push(struct active_flow **af)
{
    struct active_flow_node_t *current = NULL;

    if (head == NULL)
    {
        current = (struct active_flow_node_t *)malloc(sizeof(struct active_flow_node_t));
        current->af = *af; // QB: this should be right (?)
        current->next = NULL;
        current->prev = NULL;
        head = current;
        return;
    }

    current = head;
    while (current->next != NULL)
    {
        current = current->next;
    }

    /* now we can add a new variable */
    current->next = (struct active_flow_node_t *)malloc(sizeof(struct active_flow_node_t));
    current->next->af = *af; // QB: this should be right (?)
    current->next->next = NULL;
    current->next->prev = current;
}

// struct active_flow * pop(active_flow_node_t **head) {
//     struct active_flow * retval = -1;
//     active_flow_node_t *next_node = NULL;

//     if (*head == NULL) {
//         return -1;
//     }

//     next_node = (*head)->next;
//     retval = (*head)->af;
//     free(*head);
//     *head = next_node;

//     return retval;
// }

void remove_afnode(struct active_flow_node_t *afnode)
{
    struct active_flow_node_t *temp_node = NULL;
    if (afnode == head)
    {
        temp_node = head->next;
        free(head); // could maybe return this instead of freeing it
        head = temp_node;
        if (head != NULL) {
            head->prev = NULL;
        }
        return NULL;
    }
    // connect neighbors of afnode
    afnode->prev->next = afnode->next;
    afnode->next->prev = afnode->prev;
    free(afnode);
    return;
}

struct active_flow_node_t *search_by_index(int n, int remove)
{
    // int i = 0;
    // struct active_flow *retval = -1;
    struct active_flow_node_t *current = NULL;
    struct active_flow_node_t *temp_node = NULL;

    if (n == 0)
    {
        if (remove == 1)
        {
            // return pop(head);
            temp_node = head->next;
            // retval = (*head)->af;
            free(head); // could maybe return this instead of freeing it
            head = temp_node;
            head->prev = NULL;
            return NULL;
        }
        return head;
    }

    current = head;
    for (int i = 0; i < n - 1; i++)
    {
        if (current->next == NULL)
        {
            printf("Not enough nodes to get to index [%d]", n);
            return;
        }
        current = current->next;
    }

    // temp_node = current->next;
    // retval = temp_node->af;
    // current->next = temp_node->next;
    // free(temp_node);
    // return retval;

    if (remove == 1)
    {
        // connect neighbors of current
        current->prev->next = current->next;
        current->next->prev = current->prev;
        free(current);
        return NULL;
    }
    return current;
}

int pkts_added = 0;
long total_pkt_size = 0; // changed to long for pkt_handler_big causes was overflowing into a negative avg pkt size
const int sim_time = 1800;
const int client_arrival_rate = 1000;
int num_pkts = 0;
struct pkt_node **pkt_list = NULL;
struct active_flow **active_flows_list = NULL;
int num_active_flows = 0;
int flow_idx = 0;
pthread_mutex_t active_list_lock;
pthread_mutex_t num_active_flows_lock;
pthread_mutex_t flooder_handle_lock;

/* Functions  */
void pkt_handler_longbig(u_char *args, const struct pcap_pkthdr *pkt_hdr, const u_char *pkt)
{
    int data_sz = 1500 - sizeof(struct ether_header) - pkt_hdr->len; // extra data
    char *data;
    if (data_sz > 0)
    {
        data = (char *)calloc(data_sz, 1);
        memset(data, 0x1, data_sz - 1);
        data[data_sz - 1] = '\0';
    }
    else
    {
        // printf("less than 0");
        data_sz = 0; // dont let it be negative, messes up the length fields and avg pkt size calculation
    }

    u_char *eth_pkt = (u_char *)calloc(1, sizeof(struct ether_header) + pkt_hdr->len + data_sz);
    struct ether_header *eh = (struct ether_header *)eth_pkt;
    eh->ether_type = htons(ETH_P_IP);
    int shost0 = 0xba; // still truncated even with this
    int shost1 = 0x6e;
    int shost2 = 0xd9;
    int shost3 = 0xe7;
    int shost4 = 0x7a;
    int shost5 = 0x30;
    eh->ether_shost[0] = shost0;
    eh->ether_shost[1] = shost1;
    eh->ether_shost[2] = shost2;
    eh->ether_shost[3] = shost3;
    eh->ether_shost[4] = shost4;
    eh->ether_shost[5] = shost5;
    int dhost0 = 0x12; // still truncated even with this
    int dhost1 = 0x34;
    int dhost2 = 0x56;
    int dhost3 = 0x78;
    int dhost4 = 0x90;
    int dhost5 = 0x12;
    eh->ether_dhost[0] = dhost0;
    eh->ether_dhost[1] = dhost1;
    eh->ether_dhost[2] = dhost2;
    eh->ether_dhost[3] = dhost3;
    eh->ether_dhost[4] = dhost4;
    eh->ether_dhost[5] = dhost5;

    pkt_list[pkts_added] = (struct pkt_node *)calloc(1, sizeof(struct pkt_node));
    // pkt_list[pkts_added]->eth_pkt = (u_char *)calloc(1, pkt_hdr->len);
    pkt_list[pkts_added]->eth_pkt = eth_pkt;                                                // point node to the empty pkt in memory
    memcpy(pkt_list[pkts_added]->eth_pkt + sizeof(struct ether_header), pkt, pkt_hdr->len); // copy pkt contents into node (only pkt_hdr->len bytes of pkt)
    if (data_sz > 0)
    {                                                                                                      // only copy data bytes if necessary, prob dont need this anymore since we use else above to prevent negatives
        memcpy(pkt_list[pkts_added]->eth_pkt + sizeof(struct ether_header) + pkt_hdr->len, data, data_sz); // copy rest of data
    }
    pkt_list[pkts_added]->length = sizeof(struct ether_header) + pkt_hdr->len + data_sz; // send ether header plus IP pkt content
    pkts_added++;
    total_pkt_size += pkt_hdr->len + data_sz;
    // printf("%d\n", data_sz);
    // printf("pkt: %s\n", pkt);
}

void pkt_handler_big(u_char *args, const struct pcap_pkthdr *pkt_hdr, const u_char *pkt)
{
    int data_sz = 1500 - sizeof(struct ether_header) - pkt_hdr->len;
    char *data;
    if (data_sz > 0)
    {
        data = (char *)calloc(data_sz, 1);
        memset(data, 0x1, data_sz - 1);
        data[data_sz - 1] = '\0';
    }
    else
    {
        // printf("less than 0");
        data_sz = 0; // dont let it be negative, messes up the length fields and avg pkt size calculation
    }

    u_char *eth_pkt = (u_char *)calloc(1, sizeof(struct ether_header) + pkt_hdr->len + data_sz);
    struct ether_header *eh = (struct ether_header *)eth_pkt;
    eh->ether_type = htons(ETH_P_IP);
    int shost0 = 0xba; // still truncated even with this
    int shost1 = 0x6e;
    int shost2 = 0xd9;
    int shost3 = 0xe7;
    int shost4 = 0x7a;
    int shost5 = 0x30;
    eh->ether_shost[0] = shost0;
    eh->ether_shost[1] = shost1;
    eh->ether_shost[2] = shost2;
    eh->ether_shost[3] = shost3;
    eh->ether_shost[4] = shost4;
    eh->ether_shost[5] = shost5;
    int dhost0 = 0x12; // still truncated even with this
    int dhost1 = 0x34;
    int dhost2 = 0x56;
    int dhost3 = 0x78;
    int dhost4 = 0x90;
    int dhost5 = 0x12;
    eh->ether_dhost[0] = dhost0;
    eh->ether_dhost[1] = dhost1;
    eh->ether_dhost[2] = dhost2;
    eh->ether_dhost[3] = dhost3;
    eh->ether_dhost[4] = dhost4;
    eh->ether_dhost[5] = dhost5;

    pkt_list[pkts_added] = (struct pkt_node *)calloc(1, sizeof(struct pkt_node));
    // pkt_list[pkts_added]->eth_pkt = (u_char *)calloc(1, pkt_hdr->len);
    pkt_list[pkts_added]->eth_pkt = eth_pkt;                                                // point node to the empty pkt in memory
    memcpy(pkt_list[pkts_added]->eth_pkt + sizeof(struct ether_header), pkt, pkt_hdr->len); // copy pkt contents into node (only pkt_hdr->len bytes of pkt)
    if (data_sz > 0)
    {                                                                                                      // only copy data bytes if necessary, prob dont need this anymore since we use else above to prevent negatives
        memcpy(pkt_list[pkts_added]->eth_pkt + sizeof(struct ether_header) + pkt_hdr->len, data, data_sz); // copy rest of data
    }
    pkt_list[pkts_added]->length = sizeof(struct ether_header) + pkt_hdr->len + data_sz; // send ether header plus IP pkt content
    pkts_added++;
    total_pkt_size += pkt_hdr->len + data_sz;
    // printf("%d\n", data_sz);
    // printf("pkt: %s\n", pkt);
}

/**
 * Function     : pkt_handler
 * Description  : Handler for incoming pkts (or pkts read from pcap file).
 * 
 * Inputs       :
 * Outputs      : n/a
 */
void pkt_handler(u_char *args, const struct pcap_pkthdr *pkt_hdr, const u_char *pkt)
{
    u_char *eth_pkt = (u_char *)calloc(1, sizeof(struct ether_header) + pkt_hdr->len);
    struct ether_header *eh = (struct ether_header *)eth_pkt;
    eh->ether_type = htons(ETH_P_IP);
    int shost0 = 0xba; // still truncated even with this
    int shost1 = 0x6e;
    int shost2 = 0xd9;
    int shost3 = 0xe7;
    int shost4 = 0x7a;
    int shost5 = 0x30;
    eh->ether_shost[0] = shost0;
    eh->ether_shost[1] = shost1;
    eh->ether_shost[2] = shost2;
    eh->ether_shost[3] = shost3;
    eh->ether_shost[4] = shost4;
    eh->ether_shost[5] = shost5;
    int dhost0 = 0x12; // still truncated even with this
    int dhost1 = 0x34;
    int dhost2 = 0x56;
    int dhost3 = 0x78;
    int dhost4 = 0x90;
    int dhost5 = 0x12;
    eh->ether_dhost[0] = dhost0;
    eh->ether_dhost[1] = dhost1;
    eh->ether_dhost[2] = dhost2;
    eh->ether_dhost[3] = dhost3;
    eh->ether_dhost[4] = dhost4;
    eh->ether_dhost[5] = dhost5;

    pkt_list[pkts_added] = (struct pkt_node *)calloc(1, sizeof(struct pkt_node));
    // pkt_list[pkts_added]->eth_pkt = (u_char *)calloc(1, pkt_hdr->len);
    pkt_list[pkts_added]->eth_pkt = eth_pkt;                                                // point node to the empty pkt in memory
    memcpy(pkt_list[pkts_added]->eth_pkt + sizeof(struct ether_header), pkt, pkt_hdr->len); // copy pkt contents into node (only pkt_hdr->len bytes of pkt)
    pkt_list[pkts_added]->length = sizeof(struct ether_header) + pkt_hdr->len;              // send ether header plus IP pkt content
    pkts_added++;
    total_pkt_size += pkt_hdr->len;
    // printf("pkt: %s\n", pkt);
}

/**
 * Function     : run_flooder
 * Description  : Start flooding packets from pcap.
 * 
 * Inputs       :
 * Outputs      : n/a
 */
int run_flooder()
{
    num_pkts = sim_time * client_arrival_rate;
    pkt_list = (struct pkt_node **)calloc(num_pkts, sizeof(struct pkt_node *));
    active_flows_list = (struct active_flow **)calloc(num_pkts, sizeof(struct active_flow *));

    char error_buf1[PCAP_ERRBUF_SIZE];
    char *f = "../flooder-1000-1800.pcap";
    pcap_t *pcap_file_handle = pcap_open_offline(f, error_buf1);
    struct timeval tv_start;
    struct timeval tv2_end;
    double start_time = 0.0;
    double end_time = 0.0;

    // Step 1 - Read pcap from file
    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    pcap_loop(pcap_file_handle, num_pkts, pkt_handler, NULL);
    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Read pcap in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    printf("Packets read: %d\n", pkts_added);
    printf("Avg pkt size: %.3f bytes\n", total_pkt_size * 1.0 / num_pkts);
    pcap_close(pcap_file_handle); // close this handle for the pcap file

    // Step 2 - Flood pkts
    char error_buf2[PCAP_ERRBUF_SIZE];
    const char *dev = "uph-eth0";
    // const char *dev = "enp7s0";
    int snaplen = BUFSIZ;
    int promisc = 0;
    int timeout_lim = 10000;                                                                 // in ms
    pcap_t *flooder_handle = pcap_open_live(dev, snaplen, promisc, timeout_lim, error_buf2); // open new pcap handle for nic
    if (flooder_handle == NULL)
    {
        printf("Error finding device: %s\n", error_buf2);
        return -1;
    }

    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    for (int j = 0; j < (int)100e3; j++) // for normal flooder
    {
        for (int i = 0; i < (int)10e3; i++) // for normal flooder
        {
            int rc = pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length);
            // printf("len: %d\n", pkt_list[i]->length);
            // printf("bytes sent: %d\n", rc);
            usleep(350);
            // printf("Sent %d pkts...\n", i+1);
        }
    }

    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Flooded packets in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    pcap_close(flooder_handle);                                            // close this handle for the flooder

    return 0;
}

int run_big_flooder(int num_pkts)
{
    num_pkts = sim_time * client_arrival_rate;
    pkt_list = (struct pkt_node **)calloc(num_pkts, sizeof(struct pkt_node *));
    active_flows_list = (struct active_flow **)calloc(num_pkts, sizeof(struct active_flow *));

    char error_buf1[PCAP_ERRBUF_SIZE];
    // char *f = "../flooder-1000-1800.pcap";
    char *f = "flooder-0.01M-flows.pcap"; // uncomment this, chage pcap_loop, and change flooder loop, to use
    pcap_t *pcap_file_handle = pcap_open_offline(f, error_buf1);
    struct timeval tv_start;
    struct timeval tv2_end;
    double start_time = 0.0;
    double end_time = 0.0;

    // Step 1 - Read pcap from file
    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    // pcap_loop(pcap_file_handle, num_pkts, pkt_handler, NULL);
    pcap_loop(pcap_file_handle, num_pkts, pkt_handler_big, NULL);
    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Read pcap in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    printf("Packets read: %d\n", pkts_added);
    // printf("Avg pkt size: %.3f bytes\n", total_pkt_size*1.0/num_pkts);
    printf("Avg pkt size: %.3f bytes\n", total_pkt_size * 1.0 / 10e3);
    pcap_close(pcap_file_handle); // close this handle for the pcap file

    // Step 2 - Flood pkts
    char error_buf2[PCAP_ERRBUF_SIZE];
    const char *dev = "uph-eth0";
    // const char *dev = "enp7s0";
    int snaplen = BUFSIZ;
    int promisc = 0;
    int timeout_lim = 10000;                                                                 // in ms
    pcap_t *flooder_handle = pcap_open_live(dev, snaplen, promisc, timeout_lim, error_buf2); // open new pcap handle for nic
    if (flooder_handle == NULL)
    {
        printf("Error finding device: %s\n", error_buf2);
        return -1;
    }

    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    for (int j = 0; j < 100; j++)
    { // for big flooder
        for (int i = 0; i < (int)10e3; i++)
        {
            int rc = pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length);
            // printf("len: %d\n", pkt_list[i]->length);
            // printf("bytes sent: %d\n", rc);
            usleep(350);
            // printf("Sent %d pkts...\n", i+1);
        }
    }

    // for (int i = 0; i < (int)10e3; i++) // for normal flooder
    // {
    //     int rc = pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length);
    //     // printf("len: %d\n", pkt_list[i]->length);
    //     // printf("bytes sent: %d\n", rc);
    //     usleep(350);
    //     // printf("Sent %d pkts...\n", i+1);
    // }

    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Flooded packets in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    pcap_close(flooder_handle);                                            // close this handle for the flooder

    return 0;
}

void new_flows_runner(void *fh)
{
    int new_flows_sleep_time = 5000; // in usec
    pcap_t *flooder_handle = *((pcap_t **)fh);
    struct active_flow *af = NULL;
    // int num_flows = (int)10e3;
    // for (int i = 0; i < num_flows; i++)
    for (int i = 0; i < num_pkts; i++)
    {
        pthread_mutex_lock(&flooder_handle_lock);
        int rc = pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length); // inject once then add to active list (doesnt get sent again from here)
        // if (rc <= 0) {
        //     char *errmsg = pcap_geterr(flooder_handle);
        //     printf("%s ==== flooder_handle: %p\n", errmsg, flooder_handle);
        // }
        pthread_mutex_unlock(&flooder_handle_lock);
        // here using list/array
        pthread_mutex_lock(&active_list_lock);
        // active_flows_list[flow_idx] = (struct active_flow *)calloc(1, sizeof(struct active_flow));
        // active_flows_list[flow_idx]->duration = 10000; // TODO: not really 30s yet since we are not using sleep in active thread
        // active_flows_list[flow_idx]->time_active = 1;
        // active_flows_list[flow_idx]->pnode = pkt_list[i];
        // flow_idx++; // for assigning flows into the list

        // using linked list now instead
        af = (struct active_flow *)calloc(1, sizeof(struct active_flow));
        af->duration = 8; // TODO: not really 30s yet since we are not using sleep in active thread
        af->time_active = 1;
        af->start_time = time(NULL);
        af->pnode = pkt_list[i];
        push(&af);
        pthread_mutex_unlock(&active_list_lock);

        pthread_mutex_lock(&num_active_flows_lock);
        num_active_flows++; // dynamically changing as flows are added and expire (used to set the sleep for ACTIVE_FLOWS)
        pthread_mutex_unlock(&num_active_flows_lock);

        // printf("bytes sent: %d\n", rc);
        usleep(new_flows_sleep_time); // constant for new flows because constant arrival rate
    }
}

// #define LIMIT (1000000)
// static uint16_t highest_bit(uint64_t v) {
//     uint16_t out = 0;
//     while (v > 0) {
//         v >>= 1;
//         ++out;
//     }
//     return out;
// }

// uint32_t myrand() {
//     static bool init = 0;
//     static uint16_t n;
//     static uint16_t shift;
//     if (!init) {
//         uint16_t randbits = highest_bit(RAND_MAX + (uint64_t)1L);
//         uint16_t outbits = highest_bit(LIMIT);
//         n = (outbits + randbits - 1)/randbits;
//         shift = randbits;
//         init = 1;
//     }
//     uint32_t out = 0;
//     for (uint16_t i=0; i<n; ++i) {
//         out |= rand() << (i*shift);
//     }
//     return out % LIMIT;
// }

void active_flows_runner(void *fh)
{
    pcap_t *flooder_handle = *((pcap_t **)fh);
    // int num_flows = (int)10e3;
    int sleep_set = 0;
    int active_sleep_time = 0;
    int num_flows_sent_since_sleep_set = 0;
    uint32_t i = (uint32_t)0;
    // int counter = 0;
    usleep(30000000);
    printf("Starting active runner [%d flows]...\n", num_active_flows);
    while (1)
    {
        // for (int i = 0; i < num_flows; i++) // loop through active_list and inject any that are still active (time_active hasnt hit duration yet); should be able to get through all of them within a second, but if not then may need to use linked_list
        // for (int i = 0; i < num_pkts; i++)
        // {
        // i = (rand() % (upper – lower + 1)) + lower;
        // i = (rand() % (num_pkts - 0 + 1)) + 0;
        // i = myrand();
        pthread_mutex_lock(&active_list_lock);
        struct active_flow_node_t *inode = NULL;
        if (num_active_flows == 0)
        {
            i = 0;
            inode = search_by_index(i, 0);
            if (inode == NULL)
            { // new runner didnt get to add the flow yet (active runner moving quicker (?))
                pthread_mutex_unlock(&active_list_lock);
                continue; // just keep looping until we have something
            }
        }
        else
        {
            i = (rand() * rand()) % num_active_flows;
            inode = search_by_index(i, 0);
            // while ((active_flows_list[i] == NULL) || (active_flows_list[i]->pnode == NULL)) { // while the flow is not active yet or is expired, keep searching
            while ((inode == NULL) || (inode->af->pnode == NULL))
            {
                i = (rand() * rand()) % num_active_flows; // goes up to like 32k*32k = 1B, which should be more than enough
                inode = search_by_index(i, 0);
                // printf("searching %d\n", i);
            }
        }
        // printf("found\n");
        pthread_mutex_unlock(&active_list_lock); // active wasnt releasing lock before but this above should work
        // pthread_mutex_lock(&active_list_lock);
        // if (active_flows_list[i] == NULL)
        // { // flow not active yet
        //     pthread_mutex_unlock(&active_list_lock);
        //     // printf("%p\n", active_flows_list[i]);
        //     // printf("nope1\n");
        //     continue;
        // }
        // if (active_flows_list[i]->pnode == NULL) // if flow is expired
        // {                                        // since using calloc, unused should be init to NULL
        //     pthread_mutex_unlock(&active_list_lock);
        //     // printf("nope2\n");
        //     continue;
        // }
        // pthread_mutex_unlock(&active_list_lock);
        // printf("%p\n", inode); // was printing (nil), I assume when i was getting set to 0; we should prob just skip in the begin, because this is prob hitting before new runner can actually add the flow
        if (inode->af->time_active == inode->af->duration) // if last pkt for the flow was already sent, expire it
        {
            // printf("found2\n");
            // free(active_flows_list[i]->pnode); // dont think we need to really free the pkt_list[i]
            pthread_mutex_lock(&active_list_lock);
            inode->af->pnode = NULL; // expire the flow
            printf("%p ended in %lds\n", inode, time(NULL)-inode->af->start_time);
            remove_afnode(inode);
            pthread_mutex_unlock(&active_list_lock);

            pthread_mutex_lock(&num_active_flows_lock);
            num_active_flows--;
            pthread_mutex_unlock(&num_active_flows_lock);
            // printf("nope3\n");
        }
        else
        {
            // counter++;
            // printf("found3; sent %d pkts\n", counter);
            // otherwise inject and update time_active
            // use num_active_flows as sleep time in usec
            // lock active_flows_list
            // if (i * (num_active_flows * 1e-6) == 1)
            // { // after about 1 second, increase duration for all flows
            // }
            pthread_mutex_lock(&flooder_handle_lock);
            int rc = pcap_inject(flooder_handle, inode->af->pnode->eth_pkt, inode->af->pnode->length);
            // if (rc <= 0) {
            //     char *errmsg = pcap_geterr(flooder_handle);
            //     printf("%s ==== flooder_handle: %p\n", errmsg, flooder_handle);
            // }
            pthread_mutex_unlock(&flooder_handle_lock);
            // printf("bytes sent in active: %d\n", rc);
            inode->af->time_active++; // TODO: might need a diff way to update this...

            pthread_mutex_lock(&num_active_flows_lock);
            if (sleep_set == 0)
            { // reset inter-packet time for the next second based on the number of active_flows now
                sleep_set = 1;
                num_flows_sent_since_sleep_set = 0;
                active_sleep_time = num_active_flows;
            }
            num_flows_sent_since_sleep_set++; // means we sent another pkt (or rather are about to below)
            if (num_flows_sent_since_sleep_set == active_sleep_time)
            {                  // if we sent the correct number of packets, then about 1s has passed, so we disable this to reset pkt inter-arrival time the next iteration
                sleep_set = 0; // done sending the last batch of flows and ready to set period again
            }
            // usleep(active_sleep_time); // this will evenly space out the active flows for the next second (while new flows come in /at higher indices/)
            usleep(1000); // 1k seems to not mess up the stats collection, any faster and it stops for some reason....
            // OK with 750, OK with 500 so far... (ran f2 for a while in the beginning ~20s)
            // crashed a little after changing to 500; is it too fast or is their an IP messing things up
            pthread_mutex_unlock(&num_active_flows_lock);
        }
        // }
    }
}

int run_biglong_flooder()
{
    // num_pkts = (int)10e3;
    num_pkts = (int)1.0e6;
    // num_pkts = (int)900e3;
    pkt_list = (struct pkt_node **)calloc(num_pkts, sizeof(struct pkt_node *));
    active_flows_list = (struct active_flow **)calloc(num_pkts, sizeof(struct active_flow *));

    char *f = NULL;
    if (num_pkts == (int)10e3) // doesnt really matter if we use this or the other because we pad the pcap with data to 1500 anyway; this pcap only has 10k flows/pkts though
    {
        f = (char *)calloc(1, 25);
        memcpy(f, "flooder-0.01M-flows.pcap", 24);
        f[24] = '\0';
    }
    else if (num_pkts == (int)1.8e6)
    {
        f = (char *)calloc(1, 26);
        memcpy(f, "../flooder-1000-1800.pcap", 25);
        f[25] = '\0';
    }
    else if (num_pkts == (int)1.0e6)
    { // 1million big pkts
        f = (char *)calloc(1, 25);
        memcpy(f, "flooder-1.00M-flows.pcap", 24);
        f[24] = '\0';
    }
    else if (num_pkts == (int)900e3)
    {
        f = (char *)calloc(1, 24);
        memcpy(f, "flooder-100xm-1.1a.pcap", 23);
        f[23] = '\0';
    }
    char error_buf1[PCAP_ERRBUF_SIZE];
    pcap_t *pcap_file_handle = pcap_open_offline(f, error_buf1);
    struct timeval tv_start;
    struct timeval tv2_end;
    double start_time = 0.0;
    double end_time = 0.0;

    // Step 1 - Read pcap from file
    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    // pcap_loop(pcap_file_handle, num_pkts, pkt_handler, NULL);
    pcap_loop(pcap_file_handle, num_pkts, pkt_handler_longbig, NULL);
    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Read pcap in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    printf("Packets read: %d\n", pkts_added);
    // printf("Avg pkt size: %.3f bytes\n", total_pkt_size*1.0/num_pkts);
    // printf("Avg pkt size: %.3f bytes\n", total_pkt_size * 1.0 / 10e3);
    printf("Avg pkt size: %.3f bytes\n", total_pkt_size * 1.0 / num_pkts);
    pcap_close(pcap_file_handle); // close this handle for the pcap file

    // Step 2 - Flood pkts
    char error_buf2[PCAP_ERRBUF_SIZE];
    const char *dev = "uph-eth0";
    // const char *dev = "enp7s0";
    int snaplen = BUFSIZ;
    int promisc = 0;
    int timeout_lim = 10000;                                                                 // in ms
    pcap_t *flooder_handle = pcap_open_live(dev, snaplen, promisc, timeout_lim, error_buf2); // open new pcap handle for nic
    if (flooder_handle == NULL)
    {
        printf("Error finding device: %s\n", error_buf2);
        return -1;
    }

    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    // for (int j = 0; j < 100; j++)
    // { // for big flooder
    //     for (int i = 0; i < (int)10e3; i++)
    //     {
    //         int rc = pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length);
    //         // printf("len: %d\n", pkt_list[i]->length);
    //         // printf("bytes sent: %d\n", rc);
    //         usleep(350);
    //         // printf("Sent %d pkts...\n", i+1);
    //     }
    // }
    pthread_t new_flows_thread;
    pthread_t active_flows_thread;
    pthread_create(&new_flows_thread, NULL, new_flows_runner, &flooder_handle);
    pthread_create(&active_flows_thread, NULL, active_flows_runner, &flooder_handle);
    pthread_join(new_flows_thread, NULL);
    pthread_join(active_flows_thread, NULL);

    // for (int i = 0; i < (int)10e3; i++) // for normal flooder
    // {
    //     int rc = pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length);
    //     // printf("len: %d\n", pkt_list[i]->length);
    //     // printf("bytes sent: %d\n", rc);
    //     usleep(350);
    //     // printf("Sent %d pkts...\n", i+1);
    // }

    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Flooded packets in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    pcap_close(flooder_handle);                                            // close this handle for the flooder

    return 0;
}

unsigned short in_cksum(unsigned short *addr, int len)
{
    register int sum = 0;
    u_short answer = 0;
    register u_short *w = addr;
    register int nleft = len;
    /*
     * Our algorithm is simple, using a 32 bit accumulator (sum), we add
     * sequential 16 bit words to it, and at the end, fold back all the
     * carry bits from the top 16 bits into the lower 16 bits.
     */
    while (nleft > 1)
    {
        sum += *w++;
        nleft -= 2;
    }
    /* mop up an odd byte, if necessary */
    if (nleft == 1)
    {
        *(u_char *)(&answer) = *(u_char *)w;
        sum += answer;
    }
    /* add back carry outs from top 16 bits to low 16 bits */
    sum = (sum >> 16) + (sum & 0xffff); /* add hi 16 to low 16 */
    sum += (sum >> 16);                 /* add carry */
    answer = ~sum;                      /* truncate to 16 bits */
    return (answer);
}

int run_single_flooder()
{
    num_pkts = (int)1;
    pkt_list = (struct pkt_node **)calloc(num_pkts, sizeof(struct pkt_node *));
    char *f = "single-pkt.pcap";
    char error_buf1[PCAP_ERRBUF_SIZE];
    pcap_t *pcap_file_handle = pcap_open_offline(f, error_buf1);
    struct timeval tv_start;
    struct timeval tv2_end;
    double start_time = 0.0;
    double end_time = 0.0;

    // Step 1 - Read pcap from file
    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    pcap_loop(pcap_file_handle, num_pkts, pkt_handler_longbig, NULL);
    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Read pcap in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    printf("Packets read: %d\n", pkts_added);
    printf("Avg pkt size: %.3f bytes\n", total_pkt_size * 1.0 / num_pkts);
    pcap_close(pcap_file_handle); // close this handle for the pcap file

    // Step 2 - Flood pkts
    char error_buf2[PCAP_ERRBUF_SIZE];
    const char *dev = "uph-eth0";
    int snaplen = BUFSIZ;
    int promisc = 0;
    int timeout_lim = 10000;                                                                 // in ms
    pcap_t *flooder_handle = pcap_open_live(dev, snaplen, promisc, timeout_lim, error_buf2); // open new pcap handle for nic
    if (flooder_handle == NULL)
    {
        printf("Error finding device: %s\n", error_buf2);
        return -1;
    }

    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    for (int j = 0; j < (int)100e6; j++)
    {
        pcap_inject(flooder_handle, pkt_list[0]->eth_pkt, pkt_list[0]->length);
        // printf("bytes sent: %d\n", rc);
        // usleep(62);
        usleep(65);
        // printf("Sent %d pkts...\n", i+1);
    }

    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Flooded packets in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    pcap_close(flooder_handle);                                            // close this handle for the flooder

    return 0;
}

/**
 * Function     : run_udp_flooder
 * Description  : Generate and flood udp packets.
 * 
 * Inputs       :
 * Outputs      : n/a
 */
int run_udp_flooder()
{
    num_pkts = sim_time * client_arrival_rate;
    pkt_list = (struct pkt_node **)calloc(num_pkts, sizeof(struct pkt_node *));
    active_flows_list = (struct active_flow **)calloc(num_pkts, sizeof(struct active_flow *));

    // TODO: dont know why this function is not working
    // int sockfd;
    // struct sockaddr_in servaddr;

    // sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    // memset(&servaddr, 0, sizeof(servaddr));

    // servaddr.sin_family = AF_INET;
    // servaddr.sin_port = htons(8080);
    // servaddr.sin_addr.s_addr = INADDR_ANY;

    // const char *msg = "hello";
    // sendto(sockfd, (const char *)msg, strlen(msg), 0, &servaddr, sizeof(servaddr));

    // char sendbuf[BUF_SIZ];
    struct ether_header *eh;
    struct iphdr *ip;
    // struct iphdr *ip_reply;
    struct icmphdr *icmp;
    // struct sockaddr_in connection;
    // char *dst_addr = "192.168.1.33";
    // char *src_addr = "192.168.1.34";
    char *src_addr = "10.0.0.131";
    char *dst_addr = "10.0.0.100";
    char *packet;
    // char *buffer;
    // int sockfd, optval;
    // int addrlen;
    int data_sz = 1458; // edit 1/15: includes null at end now
    char *data = (char *)calloc(data_sz, 1);
    memset(data, 0x1, data_sz - 1); // update 1/15: reserve last byte
    data[data_sz - 1] = '\0';       // set last to null char

    packet = malloc(sizeof(struct ether_header) + sizeof(struct iphdr) + sizeof(struct icmphdr) + data_sz);
    memcpy(packet + sizeof(struct ether_header) + sizeof(struct iphdr) + sizeof(struct icmphdr), data, data_sz);
    // buffer = malloc(sizeof(struct iphdr) + sizeof(struct icmphdr));
    // ip = (struct iphdr *)packet;
    // icmp = (struct icmphdr *)(packet + sizeof(struct iphdr));
    // custom ether header
    // memset(sendbuf, 0, BUF_SIZ);
    eh = (struct ether_header *)packet;
    // eh->ether_type = htons(ETH_P_IP);
    eh->ether_type = htons(ETH_P_IP);
    int dhost0 = 0xc4; // still truncated even with this
    int dhost1 = 0x7c;
    int dhost2 = 0x16;
    int dhost3 = 0xad;
    int dhost4 = 0x65;
    int dhost5 = 0x6e;
    eh->ether_dhost[0] = dhost0;
    eh->ether_dhost[1] = dhost1;
    eh->ether_dhost[2] = dhost2;
    eh->ether_dhost[3] = dhost3;
    eh->ether_dhost[4] = dhost4;
    eh->ether_dhost[5] = dhost5;

    // custom ip header
    ip = (struct iphdr *)(packet + sizeof(struct ether_header));
    ip->ihl = 5;
    ip->version = 4;
    ip->tot_len = sizeof(struct iphdr) + sizeof(struct icmphdr) + data_sz;
    ip->ttl = 10;
    printf("\ntotal len: %u", ip->tot_len);
    printf("\nsizeof(packet): %lu", sizeof(packet));
    printf("\ntest\n");
    ip->protocol = IPPROTO_ICMP;
    ip->saddr = inet_addr(src_addr);
    ip->daddr = inet_addr(dst_addr);
    // ip->check = in_cksum((unsigned short *)ip, sizeof(struct iphdr));
    // ip->check = 0x322a;

    // custom icmp header
    // icmp = (struct icmphdr *)(ip + sizeof(struct iphdr));
    icmp = (struct icmphdr *)(packet + sizeof(struct ether_header) + sizeof(struct iphdr));
    icmp->type = ICMP_ECHO;
    // icmp->checksum = in_cksum((unsigned short *)icmp, sizeof(struct icmphdr));
    // icmp->checksum = 0x322a;
    icmp->checksum = 0x251c;

    /* open ICMP socket */
    // QB: can't modify IP headers if using socket
    // if ((sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)) == -1)
    // {
    //  perror("socket");
    //  exit(EXIT_FAILURE);
    // }
    /* IP_HDRINCL must be set on the socket so that the kernel does not attempt 
  *  to automatically add a default ip header to the packet*/
    // setsockopt(sockfd, IPPROTO_IP, IP_HDRINCL, &optval, sizeof(int));

    // connection.sin_family = AF_INET;
    // connection.sin_addr.s_addr = ip->daddr;
    // while (1)
    // {
    //  sendto(sockfd, packet, ip->tot_len, 0, (struct sockaddr *)&connection, sizeof(struct sockaddr));
    //  // printf("Sent %d byte packet to %s\n", ip->tot_len, dst_addr);
    // }

    // flood with libpcap instead
    struct timeval tv_start;
    struct timeval tv2_end;
    double start_time = 0.0;
    double end_time = 0.0;
    char error_buf2[PCAP_ERRBUF_SIZE];
    const char *dev = "uph-eth0";
    //  const char *dev = "ups-eth1";
    int snaplen = BUFSIZ;
    int promisc = 0;
    int timeout_lim = 10000;                                                                 // in ms
    pcap_t *flooder_handle = pcap_open_live(dev, snaplen, promisc, timeout_lim, error_buf2); // open new pcap handle for nic
    if (flooder_handle == NULL)
    {
        printf("Error finding device: %s\n", error_buf2);
        return -1;
    }
    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    printf("ip->tot_len: %d\n", ip->tot_len);
    // int rc = 0;
    for (int i = 0; i < num_pkts; i++)
    {
        // pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length);
        // rc = pcap_inject(flooder_handle, packet, ip->tot_len + sizeof(struct ether_header));
        pcap_inject(flooder_handle, packet, ip->tot_len + sizeof(struct ether_header));
        // printf("bytes sent: %d\n", rc);
        // sleep(1); // still truncated when sending slow
        usleep(500);
    }
    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Flooded [%d] packets in %.3fs]\n", num_pkts, (end_time - start_time) / 1e6); // back to seconds
    pcap_close(flooder_handle);

    return 0;
}

/**
 * Function     : main
 * Description  : Entry point.
 * 
 * Inputs       : argc - number of parameters
 *                argv - the parameters
 * Outputs      : 0 if success, -1 if failure
 */
int main(int argc, char *argv[])
{
    if (pthread_mutex_init(&num_active_flows_lock, NULL) != 0)
    {
        printf("error on init active_flows_lock\n");
        return -1;
    }

    if (pthread_mutex_init(&active_list_lock, NULL) != 0)
    {
        printf("error on init active_list_lock\n");
        return -1;
    }

    if (pthread_mutex_init(&flooder_handle_lock, NULL) != 0)
    {
        printf("error on init flooder_handle_lock\n");
        return -1;
    }

    // run_flooder();
    // run_big_flooder();
    // run_udp_flooder();

    run_biglong_flooder();
    // run_single_flooder();
}
